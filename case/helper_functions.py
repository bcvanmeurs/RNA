from ftplib import FTP
import os
import h5py as h5py
import numpy as np
import matplotlib.pyplot as plt
import rasterio
import multiprocessing as mp

class GPM:

    def __init__(self,local_filename, bounds = None):
        self.local_filename = local_filename
        dataset = dataset = h5py.File(local_filename, 'r') 
        precip = dataset['Grid/precipitationCal'][:]
        precip = np.transpose(precip)
        precip = precip.squeeze()
        self.precip = precip[::-1]
        self.theLats= dataset['Grid/lat'][:][::-1]
        self.theLons = dataset['Grid/lon'][:]
        if bounds is not None:
            self.set_crop(bounds)
        
    def get_grid(self):
        #masked_precip = np.ma.masked_where(precip < 0,precip)
        return self.precip
    
    def plot(self):
        masked_precip = np.ma.masked_where(self.precip < 0,self.precip)
        plt.imshow(masked_precip)
    
    def set_crop(self, bounds):
        west, south, east, north = bounds
        self.west = np.floor(west*10)/10
        self.east = np.ceil(east*10)/10
        self.south = np.floor(south*10)/10
        self.north = np.ceil(north*10)/10
        self.lonmin_ind = np.where(self.theLons > self.west)[0].min()
        self.lonmax_ind = np.where(self.theLons < self.east)[0].max()
        self.latmin_ind = np.where(self.theLats > self.south)[0].max()
        self.latmax_ind = np.where(self.theLats < self.north)[0].min()
        #print('lonmin: ' + str(self.theLons[lonmin]))
        #print('lonmax: ' + str(self.theLons[lonmax]))
        #print('latmin: ' + str(self.theLats[latmin]))
        #print('latmax: ' + str(self.theLats[latmax]))     
        
    def get_bounds(self):
        return (self.west,self.south,self.east,self.north)
    
    def get_bounds_transform(self):
        return (self.west,self.south,self.east,self.north,self.lonmax_ind-self.lonmin_ind+1,self.latmin_ind-self.latmax_ind+1)
    
    def get_crop(self):
        return self.precip[self.latmax_ind:self.latmin_ind+1,self.lonmin_ind:self.lonmax_ind+1]
    
    def plot_crop(self):
        crop = self.get_crop()
        masked_crop = np.ma.masked_where(crop < 0,crop)
        plt.imshow(masked_crop)
    
    def coordinates(self, bounds = None):
        if bounds is not None:
            return (self.theLats[self.latmax_ind:self.latmin_ind+1],self.theLons[self.lonmin_ind:self.lonmax_ind+1])
        else:
            return (self.theLats,self.theLons)
    
    def save_cropped_tif(self):
        local_filename = self.local_filename.split('/')
        local_filename[1] = 'tif'
        directory = '/'.join(local_filename[0:3])
        local_filename = '/'.join(local_filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.isfile(local_filename + '-masked.tif'):
            data = self.get_crop().astype('float32')
            transform = rasterio.transform.from_bounds(*self.get_bounds_transform())
            writer = rasterio.open( local_filename + '-masked.tif', 'w', driver='GTiff',
                                        height = data.shape[0], width = data.shape[1],
                                        count=1, dtype=str(data.dtype),
                                        crs='epsg:4326',
                                        transform=transform,
                                        nodata=-9999.9
                                )

            writer.write(data, 1)
            writer.close()
    

def pmm_ftp(date,filename):
    
    directory = 'data_pmm/raw/' + date.replace('/','-')
    local_filename = os.path.join(directory, filename)
    
    if not os.path.exists(directory):
        os.makedirs(directory)

    ftp = FTP('arthurhou.pps.eosdis.nasa.gov', user = '**fill_in**', passwd='**fill_in**')  
    ftp.cwd('gpmdata/'+ date +'/imerg')
    if True: #not os.path.isfile(local_filename):
        with open(local_filename, 'wb') as f:
            ftp.retrbinary('RETR ' + filename, f.write)
    ftp.quit()

def pmm_ftp_batch(date):
    directory = 'data_pmm/raw/' + date.replace('/','-')
    if not os.path.exists(directory):
        os.makedirs(directory)

        # add force mode
        ftp = FTP('arthurhou.pps.eosdis.nasa.gov', user = '**fill_in**', passwd='**fill_in**')  
        ftp.cwd('gpmdata/'+ date +'/imerg')
        filenames = ftp.nlst()
        filenames.sort()

        for filename in filenames:
            local_filename = os.path.join(directory, filename)
            if not os.path.isfile(local_filename):
                print('Downloading: ' + local_filename)
                with open(local_filename, 'wb') as f:
                    ftp.retrbinary('RETR ' + filename, f.write)
        ftp.quit()

def get_hdf_list(dates):
    if isinstance(dates,str):
        dates = [dates]
    local_filenames = []
    
    for date in dates:
        directory = 'data_pmm/raw/' + date.replace('/','-')
        files = os.listdir(directory)
        files = [i for i in files if '3B-HHR' in i]
        files = [i for i in files if '.tif' not in i]
        files.sort()
        local_filenames.extend([os.path.join(directory, file) for file in files ])
    
    return local_filenames

def get_hdf_list(dates):
    if isinstance(dates,str):
        dates = [dates]
    local_filenames = []
    
    for date in dates:
        directory = 'data_pmm/raw/' + date.replace('/','-')
        files = os.listdir(directory)
        files = [i for i in files if '3B-HHR' in i]
        files = [i for i in files if '.tif' not in i]
        files.sort()
        local_filenames.extend([os.path.join(directory, file) for file in files ])
    
    return local_filenames

def get_tif_list(dates):
    if isinstance(dates,str):
        dates = [dates]
    local_filenames = []

    for date in dates:
        directory = 'data_pmm/tif/' + date.replace('/','-')
        files = os.listdir(directory)
        files = [i for i in files if '3B-HHR' in i]
        files = [i for i in files if '-masked.tif' in i]
        files.sort()
        local_filenames.extend([os.path.join(directory, file) for file in files ])
    return local_filenames

def get_resampled_tif_list(dates):
    if isinstance(dates,str):
        dates = [dates]
    local_filenames = []
    
    for date in dates:
        directory = 'data_pmm/tif/' + date.replace('/','-')
        files = os.listdir(directory)
        files = [i for i in files if '3B-HHR' in i]
        files = [i for i in files if '-masked-resampled.tif' in i]
        files = [i for i in files if '.cpg' not in i]
        files = [i for i in files if '.dbf' not in i]
        files = [i for i in files if '.prj' not in i]
        files = [i for i in files if '.shp' not in i]
        files = [i for i in files if '.shx' not in i]
        files.sort()
        local_filenames.extend( [os.path.join(directory, file) for file in files ])
    return local_filenames

def resample(filename,source_to_match):
    from osgeo import gdal, gdalconst
    # Source
    src_filename = filename
    src = gdal.Open(src_filename, gdalconst.GA_ReadOnly)
    src_proj = src.GetProjection()
    src_geotrans = src.GetGeoTransform()

    # We want a section of source that matches this:
    match_filename = source_to_match
    match_ds = gdal.Open(match_filename, gdalconst.GA_ReadOnly)
    match_proj = match_ds.GetProjection()
    match_geotrans = match_ds.GetGeoTransform()
    wide = match_ds.RasterXSize
    high = match_ds.RasterYSize

    # Output / destination
    dst_filename = filename[:-4] + '-resampled.tif'
    dst = gdal.GetDriverByName('GTiff').Create(dst_filename, wide, high, 1, gdalconst.GDT_Float32)
    dst.SetGeoTransform( match_geotrans )
    dst.SetProjection( match_proj)

    # Do the work
    gdal.ReprojectImage(src, dst, src_proj, match_proj, gdalconst.GRA_NearestNeighbour)

    del dst # Flush

def rasterstat(areas,filename):
    #print(mp.current_process())
    if not os.path.exists(filename[:-4] + '.csv'):
        import pandas as pd
        #for filename in tiflist:
        print('\tWorking on: \t' + filename)
        data = rasterio.open(filename).read(1)
        avg_set = {}
        for row in areas:
            pixels = row[1]
            avg_set[row[0]] = calc_avg(pixels,data)
        pd.DataFrame.from_dict(avg_set,orient='index')\
            .rename_axis('Reach_ID')\
            .rename(columns={0:'rain'})\
            .to_csv(filename[:-4]+'.csv')
    else:
        print('\t' + filename[:-4] + '.csv' + ' already exists')

def calc_avg(pixels,grid):
    nr_pixels = len(pixels)
    summ = 0
    for x,y in pixels:
        summ += max(grid[x,y],0)
    avg = summ/nr_pixels
    return avg

def download_hydrosheds_data(url):
    import urllib
    import zipfile
    directory = 'data_hydrosheds'
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = url.split('/')[-1]
    local_filename = os.path.join(directory,filename)
    new_directory = local_filename[0:-4]

    if not os.path.exists(new_directory):
        if not os.path.isfile(local_filename):
            urllib.request.urlretrieve(url,local_filename)
        zip_ref = zipfile.ZipFile(local_filename, 'r')
        zip_ref.extractall(new_directory)
        zip_ref.close()

# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %load_ext autoreload
# %autoreload 2

import helper_functions
import multiprocessing as mp
import numpy as np
import globals
import gloric_filter
import GloricHydrosheds
import geopandas as gp
import time as time
import os

dates = globals.dates()
dates = dates[2:4]
print('Dates used: ' + str(dates))
bounds = globals.bounds(2)


def hydrosheds():
    print('Loading HydroSHEDS data')
    urls = [
        'https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/hydrosheds/sa_15s_zip_bil/as_dir_15s_bil.zip',
        'https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/hydrosheds/sa_shapefiles_zip/as_riv_15s.zip',
    ]
    for url in urls:
        helper_functions.download_hydrosheds_data(url)

    
    print('Filtering GloRiC data')
    if not os.path.exists('data_gloric'):
        os.makedirs('data_gloric')
    gloric_filename = 'data_gloric/GloRiC_v10_shapefile/GloRiC_v10.shp'
    gloric_filter.filter_gloric(gloric_filename,min_flow = 0)


def create_watershed():
    print('Creating watershed')
    destination_filename = 'data_gloric/padma_gloric_1m3_final.shp'
    if not os.path.isfile(destination_filename):
        start_id = 41067217
        gloric_orig = gp.read_file('data_gloric/gloric_asia_1m3.shp')
        gloric = gloric_orig.copy()
        gloric = gloric.set_index('Reach_ID',drop=False)
        
        print('\tCreating spatial index')
        start = time.time()
        spatial_index = gloric.sindex
        end = time.time()
        print('\t\tDuration: '+ '{:.2f}'.format(end - start) + 's')
        id_set = GloricHydrosheds.get_watershed(spatial_index,gloric,start_id)
        selection = gloric.loc[id_set]
        selection.to_file(destination_filename)


river_location = 'data_gloric/padma_gloric_1m3_final.shp'
direction_location = 'data_hydrosheds/as_dir_15s_bil/as_dir_15s-masked.bil'


def mask_direction_data():
    print('Masking flow direction data')
    if not os.path.isfile(direction_location):
        import rasterio.mask
        from shapely.geometry import box
        west, south, east, north = globals.bounds(1)
        polygon = box(west,south,east,north)

        data = rasterio.open('data_hydrosheds/as_dir_15s_bil/as_dir_15s.bil')
        out_image, out_transform = rasterio.mask.mask(data, [polygon], crop=True)
        out_meta = data.meta.copy()
        out_meta.update({"height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})
        with rasterio.open(direction_location, "w", **out_meta) as dest:
            dest.write(out_image)

        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})
        with rasterio.open('data_hydrosheds/as_dir_15s_bil/as_dir_15s-masked.tif', "w", **out_meta) as dest:
            dest.write(out_image)


def create_micro_watersheds():
    # not tested
    print('Create micro watersheds')
    if not os.path.isfile('data_gloric/areas_gloric.shp'):   
        from River import RiverData
        from River import RiverSegment

        data = RiverData(river_location,direction_location)
        RiverSegment.data = data
        padma = data.river.copy()

        start = time.time()
        total = len(padma.index)
        i=0
        for segment_id in padma.index:
            riversegment = RiverSegment(segment_id)
            #polygon = riversegment.get_area_pixels()
            #padma.loc[segment_id,'polygon'] = [polygon]
            polygon = riversegment.get_area_polygon()
            padma.loc[segment_id,'polygon'] = polygon
            i = i + 1
            print("\tReach number: {} {:.2f}%".format(
                str(i),
                i/total * 100,
            ),
                 end ='\r')
        end = time.time()
        print(end - start)
        area = padma.copy()
        area = area.drop('geometry',axis=1)
        area = area.rename(columns={'polygon':'geometry'})
        area.to_file("data_gloric/areas_gloric.shp")


def create_micro_watersheds_pixels():
    # not tested
    import pandas as pd
    print('Create micro watersheds pixels')
    if not os.path.isfile('data_gloric/areas_gloric_pixel.pkl'):   
        from River import RiverData
        from River import RiverSegment

        data = RiverData(river_location,direction_location)
        RiverSegment.data = data
        padma = data.river.copy()

        start = time.time()
        total = len(padma.index)
        i=0
        for segment_id in padma.index:
            riversegment = RiverSegment(segment_id)
            pixels = riversegment.get_area_pixels()
            padma.loc[segment_id,'pixels'] = [pixels]
            #polygon = riversegment.get_area_polygon()
            #padma.loc[segment_id,'polygon'] = polygon
            i = i + 1
            print("\tReach number: {} {:.2f}%".format(
                str(i),
                i/total * 100,
            ),
                 end ='\r')
        end = time.time()
        print(end - start)
        area = padma.copy()
        area = area.drop('geometry',axis=1)
        pd.DataFrame(area).to_pickle('data_gloric/areas_gloric_pixel.pkl')


from helper_functions import pmm_ftp_batch
def ftp():
    print("Retrieving Rainfall Data")
    pool=mp.Pool(1) #mp.cpu_count())  #ftp has maximum connection of 1
    pool.map(pmm_ftp_batch,dates)


def create_geo_tifs():
    print('Cropping and saving rainfall data as geo tiffs')
    filenames_rain = helper_functions.get_hdf_list(dates)
    gpm_data = helper_functions.GPM(filenames_rain[0],bounds)
    newLats, newLons = gpm_data.coordinates(bounds)
    total_rain = np.zeros(gpm_data.get_crop().shape)
    for filename in filenames_rain:
        gpm_data = helper_functions.GPM(filename,bounds)
        gpm_data.save_cropped_tif()
        total_rain += gpm_data.get_crop()
    total_rain = total_rain/2
    # Todo: save total_rain data


def resample_geo_tifs():
    print('Resampling geo tifs')
    tif_list = helper_functions.get_tif_list(dates)
    match_file = 'data_hydrosheds/as_dir_15s_bil/as_dir_15s-masked.tif'
    for local_filename in tif_list:
        if not os.path.isfile(local_filename[:-4] + '-resampled.tif'):
            helper_functions.resample(local_filename,match_file) 


def rasterstats():
    print('Determining rasterstats')
    import pandas as pd
    from itertools import repeat
    tif_list = helper_functions.get_resampled_tif_list(dates)
    areas = pd.read_pickle('data_gloric/areas_gloric_pixel.pkl')[['Reach_ID','pixels']].to_numpy()
    tif_list_remaining = [file for file in tif_list if not os.path.exists(file[:-4] + '.csv')]
    if len(tif_list_remaining) > 0:
        print('\tSpinning up pool')
        pool=mp.Pool(mp.cpu_count()-2)
        pool.starmap(helper_functions.rasterstat,zip(repeat(areas),tif_list_remaining))


def check_csvs():
    csvs = [file[:-4] + '.csv' for file in helper_functions.get_resampled_tif_list(dates)]
    import pandas as pd
    for csv in csvs:
        data = pd.read_csv(csv)
        if (data.shape != (64915,2)):
            print(csv)
        #print(data.rain.sum())


def merge_csvs():
    print('Merging csv\'s')
    csvs = [file[:-4] + '.csv' for file in helper_functions.get_resampled_tif_list(dates)]
    if not os.path.exists('data_pmm/' + csvs[0][45:69] + '-' + csvs[-1][45:69] + '.csv'):
        import pandas as pd
        data = pd.read_csv(csvs[0])
        data.set_index('Reach_ID',inplace=True)
        data.rename(columns ={'rain': csvs[0][45:69]} ,inplace=True)
        for csv in csvs[1:]:
            data = data.join(
                pd.read_csv(csv)\
                    .set_index('Reach_ID')\
                    .rename(columns ={'rain': csv[45:69]} )
            )
        data.to_csv('data_pmm/' + csvs[0][45:69] + '-' + csvs[-1][45:69] + '.csv')


def sum_csv():
    print('Sum csv')
    csvs = [file[:-4] + '.csv' for file in helper_functions.get_resampled_tif_list(dates)]
    if not os.path.exists('data_pmm/totals-' + csvs[0][45:69] + '-' + csvs[-1][45:69] + '.csv'):
        data = pd.read_csv('data_pmm/' + csvs[0][45:69] + '-' + csvs[-1][45:69] + '.csv')
        data = data.set_index('Reach_ID').sum(axis='columns').rename('total_rain')
            #data.to_csv('data_pmm/totals-' + csvs[0][45:69] + '-' + csvs[-1][45:69] + '.csv',header=True)

        areas = gp.read_file('data_gloric/areas_gloric.shp')\
                    .set_index('Reach_ID',drop=False)\
                    .loc[:,['geometry']]\
                    .join(data)\
                    .reset_index()
        areas.to_file('data_pmm/totals-' + csvs[0][45:69] + '-' + csvs[-1][45:69] + '.shp')


if __name__ == "__main__":
    print('Proces started')
    hydrosheds()
    create_watershed()
    mask_direction_data()
    create_micro_watersheds()
    create_micro_watersheds_pixels()
    ftp()
    create_geo_tifs()
    resample_geo_tifs()    
    rasterstats()
    # check_csvs()
    merge_csvs()
    sum_csv()

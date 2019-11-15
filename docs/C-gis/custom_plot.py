from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import matplotlib.font_manager as fm
import globals
import matplotlib
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import numpy as np

def base_map(figsize=(4,3)):

    fig = plt.figure(dpi=300,figsize=figsize)
    #fig = plt.figure(dpi=300,figsize=(9.3,6.2))

    crs = ccrs.PlateCarree()
    ax = plt.axes(projection=crs)

    bounds = globals.bounds(0.2)
    west, south, east, north = bounds
    south -= 1.2
    ax.set_extent([west, east, south, north])

    ax.set_xticks(range(int(np.ceil(west)+1), int(np.floor(east)+1), 2), crs=ccrs.PlateCarree())
    ax.set_yticks(range(int(np.ceil(south)), int(np.floor(north)), 2), crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.xaxis.tick_top()
    ax.tick_params(which='both',direction="in",width=0.5,length=2)
    

    matplotlib.rcParams.update({"font.size":6.0, 
                                'lines.linewidth':0.6, 
                                'patch.linewidth':0.5, 
                                "axes.titlesize":6, 
                                "axes.labelsize":6, 
                                'xtick.labelsize':4, 
                                'ytick.labelsize':4, 
                                'legend.fontsize':6 ,  
                                'pgf.rcfonts' : False})

    x = np.floor(east)
    y = np.ceil(south)-0.3
    plt.arrow(x,y,0,1,length_includes_head=True,width=0.05,head_width=0.2,facecolor='k')
    plt.text(x+0.4,y+0.4,'N',size=5,va='center',ha='center')

    fontprops = fm.FontProperties(size=4)
    asb = AnchoredSizeBar(ax.transData,
                          2,
                          '200 km',
                          loc=3,
                          label_top=True,
                          pad=0.1, borderpad=0.6, sep=1,
                          frameon=False,
                          fontproperties=fontprops,
                          size_vertical=0.07
                          )
    ax.add_artist(asb)
    

    #rivernetwork_crs.plot(ax=ax,color='b',linewidth=0.15)

    return(fig,ax)

def plot_map(facecolor = False, figsize=(4,3)):
    fig,ax = base_map(figsize)

    if not facecolor:
        face_land = face_ocean = 'none'
    elif facecolor:
        face_land = '#efefdb'
        face_ocean = '#a3dafc'

    land = cfeature.NaturalEarthFeature('cultural', 'admin_0_countries', '10m',
                                            edgecolor='k',linewidth = 0.3,facecolor=face_land ) #efefdb, #e9ebe0
    ocean = cfeature.NaturalEarthFeature('physical', 'ocean', '10m',
                                            edgecolor='k',linewidth = 0.3,facecolor=face_ocean )

    bounds = globals.bounds(0.2)
    west, south, east, north = bounds
    south -= 1.2
    x = np.floor(east)
    y = np.ceil(south)-0.3 

    ax.add_feature(land)
    ax.add_feature(ocean)
    plt.arrow(x,y,0,1,length_includes_head=True,width=0.05,head_width=0.2,facecolor='k')
    
    return(fig,ax)

def plot_river_map(dataframe,figsize=(4,3)):
    fig,ax = plot_map(figsize)

    crs_proj4 = ax.projection.proj4_init
    dataframe.to_crs(crs_proj4).plot(ax=ax,color='b',linewidth=0.15)

    
    return(fig,ax)

from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import matplotlib.font_manager as fm
import globals
import matplotlib
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import numpy as np

def base_map(figsize=(4,3),printoption = False):

    if printoption:
        fig = plt.figure(dpi=600,figsize=figsize)
    else:
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
    
    if printoption == False:
        matplotlib.rcParams.update({"font.size":6.0, 
                                    #'lines.linewidth':0.6, 
                                    'patch.linewidth':0.5, 
                                    "axes.titlesize":6, 
                                    "axes.labelsize":4, 
                                    'xtick.labelsize':4, 
                                    'ytick.labelsize':4, 
                                    'legend.fontsize':4 ,  
                                    'pgf.rcfonts' : False})
    elif printoption == True:
        print('Selected print option')
        matplotlib.rcParams.update({"font.size":6.0, 
                                    #'lines.linewidth':0.6, 
                                    'patch.linewidth':0.5, 
                                    "axes.titlesize":6, 
                                    "axes.labelsize":6, 
                                    'xtick.labelsize':6, 
                                    'ytick.labelsize':6, 
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

    return(fig,ax)

def plot_map(facecolor = False, figsize=(4,3), printoption = False):
    fig,ax = base_map(figsize, printoption = printoption)

    if not facecolor:
        face_land = face_ocean = 'none'
    elif facecolor:
        face_land = '#efefdb'
        face_ocean = '#a3dafc'
    

    land = cfeature.NaturalEarthFeature('cultural', 'admin_0_countries', '50m',
                                            edgecolor='k',linewidth = 0.3,facecolor=face_land ) #efefdb, #e9ebe0
    ocean = cfeature.NaturalEarthFeature('physical', 'ocean', '50m',
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

def plot_river_map(dataframe,figsize=(4,3), printoption = False, filename = False):
    fig,ax = plot_map(facecolor = True, figsize=figsize, printoption=printoption)

    range_min = 0.025
    range_max = 0.5
    logflow = dataframe['Log_Q_avg']
    flow = 10**logflow
    logflow = np.log10(flow + 1)
    width = ((logflow - logflow.min())*(range_max - range_min)) / (logflow.max()-logflow.min()) + range_min

    crs_proj4 = ax.projection.proj4_init
    dataframe.to_crs(crs_proj4).plot(ax=ax,color='b',linewidth=width,legend=True)
    
    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color='b', lw=0.5),]
    ax.legend(custom_lines, ['River reach'])

    if filename: plt.savefig(filename, bbox_inches = 'tight')

    return(fig,ax)

def plot_river_map_2(dataframe, split = 200, figsize=(4,3),printoption = False, filename = False):
    fig,ax = plot_map(facecolor = True, figsize=figsize, printoption = printoption)

    logsplit = np.log10(split)
    if printoption:
        range_max = 0.6
        range_min = 0.05
    else :
        range_max = 0.4
        range_min = 0.025
    logflow = dataframe['Log_Q_avg']
    flow = 10**logflow
    logflow = np.log10(flow + 1)
    width = ((logflow - logflow.min())*(range_max - range_min)) / (logflow.max()-logflow.min()) + range_min
    dataframe['linewidth'] = width

    crs_proj4 = ax.projection.proj4_init
    dataframe = dataframe.to_crs(crs_proj4)
    
    data1 = dataframe[dataframe['Log_Q_avg'] <= logsplit]
    width1 = data1['linewidth']
    data1.plot(ax=ax,color='b',linewidth=width1)

    data2 = dataframe[dataframe['Log_Q_avg'] > logsplit]
    width2 = data2['linewidth'] 
    data2.plot(ax=ax,color='r',linewidth=width2)
    
    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color='b', lw=0.3),
                    Line2D([0], [0], color='r', lw=0.5),]
    ax.legend(custom_lines, ['River reach','Avg flow > ' + str(split) + ' m$^3$/s'])

    bounds = globals.bounds(0.2)
    west, south, east, north = bounds
    north += 1
    south -= 1.2
    ax.set_extent([west, east, south, north])
    ax.set_yticks(range(int(np.ceil(south)), int(np.floor(north))+1, 2), crs=ccrs.PlateCarree())

    if filename: 
        plt.title("Watershed created from Gloric dataset")
        plt.savefig(filename, bbox_inches = 'tight')

    return(fig,ax)

def plot_results_map(dataframe,figsize=(4,3),printoption = False, filename = False):
    fig,ax = plot_map(facecolor=False,figsize=figsize,printoption=printoption)


    # transform data
    crs_proj4 = ax.projection.proj4_init
    dataframe = dataframe.to_crs(crs_proj4)
    max_overflow = dataframe

    # scale width and set color
    range_min = 0.2
    range_max = 0.6
    flow = max_overflow['max_overflow']
    logflow = np.log10(max_overflow['max_overflow'] + 1)
    width = ((logflow - logflow.min())*(range_max - range_min)) / (logflow.max()-logflow.min()) + range_min

    from matplotlib import cm
    norm = cm.colors.LogNorm(vmax=flow.max(), vmin=1)
    cmap = cm.get_cmap('RdYlGn').reversed() # jet #RdYlGn
    cmap.set_bad(cmap(0.0))
    color = flow.apply(norm).apply(cmap)        

    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(ax)
    plt.title('Model results June 16 - 17, 2013')
    
    cax2 = divider.append_axes("bottom", size=0.05, pad=0.05, axes_class=plt.Axes)
    max_overflow.plot(ax=ax , linewidth = width , color = color)
    cb = plt.colorbar(plt.cm.ScalarMappable(norm,cmap),cax=cax2, orientation='horizontal',label = 'Overflow [m$^3$/s]')

    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color='k', lw=0.5)]
    ax.legend(custom_lines, ['River reach'])

    if filename: plt.savefig(filename, bbox_inches = 'tight')

    return(fig,ax)

def plot_results_map_rain(dataframe,rain_data,figsize=(4,3),printoption = False, filename = False):
    fig,ax = plot_map(facecolor= False, figsize = figsize, printoption = printoption)

    total_rain, newLats, newLons = rain_data

    # transform data
    crs_proj4 = ax.projection.proj4_init
    dataframe = dataframe.to_crs(crs_proj4)
    max_overflow = dataframe

    # scale width and set color
    range_min = 0.2 #0.1
    range_max = 0.6 #0.4
    flow = max_overflow['max_overflow']
    logflow = np.log10(max_overflow['max_overflow'] + 1)
    width = ((logflow - logflow.min())*(range_max - range_min)) / (logflow.max()-logflow.min()) + range_min

    from matplotlib import cm
    norm = cm.colors.LogNorm(vmax=flow.max(), vmin=1)
    cmap = cm.get_cmap('RdYlGn').reversed() # jet #RdYlGn
    cmap.set_bad(cmap(0.0))
    color = flow.apply(norm).apply(cmap)        

    # rain data
    x, y = np.float32(np.meshgrid(newLons, newLats))
    cmap_rain = cm.get_cmap('Blues') #cm.GMT_drywet
    cbounds = np.arange(0,201,25)
    cf = plt.contourf(x,y,total_rain,cmap = cmap_rain,levels=cbounds,extend='max',alpha=0.7)

    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(ax)
    plt.title('Model results June 16 - 17, 2013')

    cax = divider.append_axes("right", size=0.05, pad=0.05, axes_class=plt.Axes)
    fig.colorbar(cf, cax=cax, label='Rain [mm]')
    
    cax2 = divider.append_axes("bottom", size=0.05, pad=0.05, axes_class=plt.Axes)
    max_overflow.plot(ax=ax , linewidth = width , color = color)
    cb = plt.colorbar(plt.cm.ScalarMappable(norm,cmap),cax=cax2, orientation='horizontal',label = 'Overflow [m$^3$/s]')

    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color='k', lw=0.5)]
    ax.legend(custom_lines, ['River reach'])

    if filename: 
        plt.savefig(filename, bbox_inches = 'tight')

    return(fig,ax)
import numpy as np
import rasterio
from rasterio.plot import show
import pandas as pd
import geopandas as gp
from shapely.geometry import Point
from shapely.geometry import box
import matplotlib.pyplot as plt
import math
from descartes import PolygonPatch

class RiverData:
    def __init__(self,river_location, direction_location):
        self.river = gp.read_file(river_location)
        self.river = self.river.set_index('Reach_ID',drop=False)
        self.spatial_index = self.river.sindex
        self.direction = rasterio.open(direction_location)
        self.direction_raster = self.direction.read(1)
        self.pixelwidth = self.direction.transform[0]

class RiverSegment:
    # https://www.toptal.com/python/python-class-attributes-an-overly-thorough-guide
    data = ''

    def __init__(self, segment_id):
        self.segment_id = segment_id

        # Load data from object
        self.river = self.data.river
        self.direction = self.data.direction
        self.direction_raster = self.data.direction_raster
        self.pixelwidth = self.data.pixelwidth

        self.geometry = self.river.loc[segment_id]['geometry']
        self.coords = self.geometry.coords[:]
        

    def get_xy(self):
        return [self.direction.index(x,y) for (x,y) in self.coords]
    
    def has_inflow(self):
        return (len(get_inflow_arcid(self.data.spatial_index,self.river,self.segment_id)) > 0)

    def get_area_pixels(self):
        x,y = get_last_pixel(self.coords,self.pixelwidth)
        row, col = self.direction.index(x,y)

        if self.has_inflow():
            x_begin, y_begin = self.coords[0]
            row_begin,col_begin = self.direction.index(x_begin,y_begin)
            inflow_ids = get_inflow_arcid(self.data.spatial_index,self.river,self.segment_id)
            end_directions = [get_end_direction(segment_id,self.river) for segment_id in inflow_ids]

            i=0
            inflow_cells = []
            search = []
            rowcol = (row,col)
            search_set = {rowcol}
            inflow_cells = search_set.copy()

            while search_set:
                new_search_set = set()
                for rowcol in search_set.copy():
                    if (rowcol[0] == row_begin) & (rowcol[1] ==col_begin):
                        new_search_set.update(find_inflow_cells_exclude_direction(rowcol,end_directions,self.direction_raster))
                    else:
                        new_search_set.update(find_inflow_cells(rowcol,self.direction_raster))
                    if new_search_set:
                        inflow_cells.update(new_search_set)
                        search_set.update(new_search_set)
                    search_set.remove(rowcol)
                    i=i+1
                    #print(i, end="\r")
            return inflow_cells 

        else:
            i=0
            inflow_cells = []
            search = []
            rowcol = (row,col)
            search_set = {rowcol}
            inflow_cells = search_set.copy()

            while search_set:
                new_search_set = set()
                for rowcol in search_set.copy():
                    new_search_set.update(find_inflow_cells(rowcol,self.direction_raster))
                    if new_search_set:
                        inflow_cells.update(new_search_set)
                        search_set.update(new_search_set)
                    search_set.remove(rowcol)
                    i=i+1
                    #print(i, end="\r")
            return inflow_cells
    
    def pixel2square(self,rowcol):
        row,col = rowcol
        x,y = self.direction.xy(row,col)
        west = x - self.pixelwidth/2
        east = x + self.pixelwidth/2
        south = y - self.pixelwidth/2
        north = y + self.pixelwidth/2
        return (west,south,east,north)
    
    def get_pixel_polygon(self,rowcol):
        west,south,east,north = self.pixel2square(rowcol)
        polygon = box(west,south,east,north)
        return polygon
    
    def get_area_polygon(self):
        geometry = [self.get_pixel_polygon(rowcol) for rowcol in self.get_area_pixels()] 
        inflow_area = gp.GeoDataFrame(geometry = geometry, crs = self.river.geometry.crs)
        polygon = inflow_area.buffer(1E-14).unary_union
        return polygon

    def show(self):
        fig,ax = plt.subplots(1,figsize=(7,7))
        # show raster with directions
        show(self.direction,ax=ax)
        # show river vector
        self.river.loc[[self.segment_id]].plot(ax=ax)

        # plot first and last pixel
        last_pixel = get_last_pixel(self.coords,self.pixelwidth)
        first_pixel = get_first_pixel(self.coords,self.pixelwidth)
        gp.GeoDataFrame( geometry = [Point(x) for x in [last_pixel,first_pixel]], crs = self.river.geometry.crs).plot(ax=ax)

        # determine bounds
        west, south, east, north = self.river.loc[[self.segment_id]].total_bounds
        pixelwidth = self.pixelwidth
        ax.set_xlim(west-pixelwidth*2, east+pixelwidth*2)
        ax.set_ylim(south-pixelwidth*2, north+pixelwidth*2)
        plt.show()

    def show_area(self):
        fig,ax = plt.subplots(1,figsize=(7,7))
        # show raster with directions
        show(self.direction,ax=ax)
        # show river vector
        self.river.loc[[self.segment_id]].plot(ax=ax)
        
        # plot area
        inflow_cells = self.get_area_pixels()
        inflow_degree = [self.direction.xy(row,col) for (row,col) in inflow_cells]
        inflow_area = gp.GeoDataFrame( geometry = [Point(x) for x in inflow_degree], crs = self.river.geometry.crs)
        inflow_area.plot(ax=ax)

        # determine bounds
        west, south, east, north = inflow_area.total_bounds
        pixelwidth = self.pixelwidth
        ax.set_xlim(west-pixelwidth*2, east+pixelwidth*2)
        ax.set_ylim(south-pixelwidth*2, north+pixelwidth*2)
        plt.show() 

    def show_area_polygon(self):
        fig,ax = plt.subplots(1,figsize=(7,7))
        # show raster with directions
        show(self.direction,ax=ax)
        # show river vector
        self.river.loc[[self.segment_id]].plot(ax=ax)
        
        # plot area
        #geometry = [self.get_pixel_polygon(rowcol) for rowcol in self.get_area_pixels()]
        #inflow_area = gp.GeoDataFrame(geometry = geometry, crs = self.river.geometry.crs)
        #inflow_area.plot(ax=ax)

        # plot area via direct polygon
        # polygon = self.get_area_polygon()
        #patch = PolygonPatch(polygon)
        #ax.add_patch(patch)


        #plot only exterior
        polygon = self.get_area_polygon()
        x,y = polygon.exterior.xy
        ax.plot(x,y,color='red')

        # determine bounds
        west, south, east, north = polygon.bounds
        pixelwidth = self.pixelwidth
        ax.set_xlim(west-pixelwidth*2, east+pixelwidth*2)
        ax.set_ylim(south-pixelwidth*2, north+pixelwidth*2)
        plt.show() 
    

    
def get_inflow(spatial_index, gdf, arcid):
    line = gdf.loc[arcid]['geometry']
    possible_matches_index = list(spatial_index.intersection(line.bounds))
    possible_matches = gdf.iloc[possible_matches_index]
    precise_matches = possible_matches[possible_matches.intersects(line.boundary[0])]
    return precise_matches

def get_inflow_arcid(spatial_index, gdf, arcid):
    matches = get_inflow(spatial_index, gdf, arcid)
    ids = set(matches.index)
    ids.remove(arcid)
    return ids

def get_neighbours(rowcol):
    row = rowcol[0]
    col = rowcol[1]
    up = (row-1,col)
    down = (row+1,col)
    left = (row,col-1)
    right = (row,col+1)
    upleft = (row-1,col-1)
    upright = (row-1,col+1)
    downleft = (row+1,col-1)
    downright = (row+1,col+1)
    neighbours = [right,downright,down,downleft,left,upleft,up,upright]
    return neighbours
    
def find_inflow_cells(rowcol, band):
    inflow_cells = []
    row = rowcol[0]
    col = rowcol[1]
    up = (row-1,col)
    if band[up[0],up[1]] == 4:
        inflow_cells.append(up)
    down = (row+1,col)
    if band[down[0],down[1]] == 64:
        inflow_cells.append(down)
    left = (row,col-1)
    if band[left[0],left[1]] == 1:
        inflow_cells.append(left)
    right = (row,col+1)
    if band[right[0],right[1]] == 16:
        inflow_cells.append(right)
    upleft = (row-1,col-1)
    if band[upleft[0],upleft[1]] == 2:
        inflow_cells.append(upleft)
    upright = (row-1,col+1)
    if band[upright[0],upright[1]] == 8:
        inflow_cells.append(upright)
    downleft = (row+1,col-1)
    if band[downleft[0],downleft[1]] == 128:
        inflow_cells.append(downleft)
    downright = (row+1,col+1)
    if band[downright[0],downright[1]] == 32:
        inflow_cells.append(downright)
    return inflow_cells

def find_inflow_cells_exclude_direction(rowcol, end_directions, band):
    inflow_cells = []
    row = rowcol[0]
    col = rowcol[1]

    if not 4 in end_directions:
        up = (row-1,col)
        if band[up[0],up[1]] == 4:
            inflow_cells.append(up)
    if not 64 in end_directions:
        down = (row+1,col)
        if band[down[0],down[1]] == 64:
            inflow_cells.append(down)
    if not 1 in end_directions:
        left = (row,col-1)
        if band[left[0],left[1]] == 1:
            inflow_cells.append(left)
    if not 16 in end_directions:
        right = (row,col+1)
        if band[right[0],right[1]] == 16:
            inflow_cells.append(right)
    if not 2 in end_directions:
        upleft = (row-1,col-1)
        if band[upleft[0],upleft[1]] == 2:
            inflow_cells.append(upleft)
    if not 8 in end_directions:
        upright = (row-1,col+1)
        if band[upright[0],upright[1]] == 8:
            inflow_cells.append(upright)
    if not 128 in end_directions:
        downleft = (row+1,col-1)
        if band[downleft[0],downleft[1]] == 128:
            inflow_cells.append(downleft)
    if not 32 in end_directions:
        downright = (row+1,col+1)
        if band[downright[0],downright[1]] == 32:
            inflow_cells.append(downright)
    return inflow_cells

def get_difference(coord1,coord2):
    x_diff = coord2[0] - coord1[0]
    y_diff = coord2[1] - coord1[1]
    return (x_diff,y_diff)

def get_direction(coord1,coord2):
    x_diff, y_diff = get_difference(coord1,coord2)
    if (x_diff > 0) & math.isclose(y_diff, 0, rel_tol=0.004166666666667):
        return 1
    elif (x_diff > 0) & (y_diff < 0):
        return 2
    elif math.isclose(x_diff, 0, rel_tol=0.004166666666667) & (y_diff < 0):
        return 4
    elif (x_diff < 0) & (y_diff < 0):
        return 8
    elif (x_diff < 0) & math.isclose(y_diff, 0, rel_tol=0.004166666666667):
        return 16
    elif (x_diff < 0) & (y_diff > 0):
        return 32
    elif math.isclose(x_diff, 0, rel_tol=0.004166666666667) & (y_diff > 0):
        return 64
    elif (x_diff > 0) & (y_diff > 0):
        return 128

def get_end_direction(arcid,gdf):
    line = gdf.loc[arcid]['geometry'].coords[:]
    return(get_direction(line[-2],line[-1]))

def get_first_pixel(points,pixelwidth):
    direction = get_direction(points[0],points[1])
    starting_point = points[0]
    if direction == 1:
        first_pixel = (starting_point[0]+pixelwidth,starting_point[1])
    elif direction == 2:
        first_pixel = (starting_point[0]+pixelwidth,starting_point[1]-pixelwidth)
    elif direction == 4:
        first_pixel = (starting_point[0],starting_point[1]-pixelwidth)
    elif direction == 8:
        first_pixel = (starting_point[0]-pixelwidth,starting_point[1]-pixelwidth)
    elif direction == 16:
        first_pixel = (starting_point[0]-pixelwidth,starting_point[1])
    elif direction == 32:
        first_pixel = (starting_point[0]-pixelwidth,starting_point[1]+pixelwidth)
    elif direction == 64:
        first_pixel = (starting_point[0],starting_point[1]+pixelwidth)
    elif direction == 128:
        first_pixel = (starting_point[0]+pixelwidth,starting_point[1]+pixelwidth)
    return first_pixel

def get_last_pixel(points,pixelwidth):
    direction = get_direction(points[-2],points[-1])
    starting_point = points[-1]
    if direction == 1:
        first_pixel = (starting_point[0]-pixelwidth,starting_point[1])
    elif direction == 2:
        first_pixel = (starting_point[0]-pixelwidth,starting_point[1]+pixelwidth)
    elif direction == 4:
        first_pixel = (starting_point[0],starting_point[1]+pixelwidth)
    elif direction == 8:
        first_pixel = (starting_point[0]+pixelwidth,starting_point[1]+pixelwidth)
    elif direction == 16:
        first_pixel = (starting_point[0]+pixelwidth,starting_point[1])
    elif direction == 32:
        first_pixel = (starting_point[0]+pixelwidth,starting_point[1]-pixelwidth)
    elif direction == 64:
        first_pixel = (starting_point[0],starting_point[1]-pixelwidth)
    elif direction == 128:
        first_pixel = (starting_point[0]-pixelwidth,starting_point[1]-pixelwidth)
    return first_pixel
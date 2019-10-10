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

def get_watershed(spatial_index,geodataframe,startid):
    i = 0
    search_set = {startid}
    network_set = search_set.copy()

    import time
    start = time.time()

    while search_set:
        new_search_set = set()
        for arcid in search_set.copy():
            new_search_set.update(get_inflow_arcid(spatial_index,geodataframe,arcid))
            if new_search_set:
                network_set.update(new_search_set)
            search_set.remove(arcid)
            i=i+1
            print(i, end="\r")
        if new_search_set:
            search_set.update(new_search_set)
            
    end = time.time()
    print('Duration: '+ '{:.2f}'.format(end - start) + 's')
    return network_set
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

import fiona
import geopandas as gp
import time
import os

filename = 'data_gloric/GloRiC_v10_shapefile/GloRiC_v10.shp'


def filter_gloric(filename, min_flow):
    dest_file = 'data_gloric/gloric_asia_1m3.shp'
    if not os.path.isfile(filename):
        with fiona.open(filename) as shapes:
            source_driver = shapes.driver
            source_crs = shapes.crs
            source_schema = shapes.schema

            start = time.time()

            #filtered = []
            i = 0
            total = len(shapes)

            with fiona.open(
             dest_file,
             'w',
             driver=source_driver,
             crs=source_crs,
             schema=source_schema) as destination:

                for shape in shapes:
                    reach_id = shape['properties']['Reach_ID']
                    avg_flow = shape['properties']['Log_Q_avg']
                    if (str(reach_id)[0] == '4') & (avg_flow > min_flow):
                        #filtered.append(shape)
                        destination.write(shape)
                    i = i+1
                    print("{} {:.2f}%".format(
                        str(i),
                        i/total * 100,
                    ),
                         end ='\r')

            end = time.time()
            print(end - start)
            shapes.close()


if __name__ == "__main__":
    filter_gloric(filename, min_flow = 0)



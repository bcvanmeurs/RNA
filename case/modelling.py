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

# %matplotlib inline
# %load_ext autoreload
# %autoreload 2

from RiverNetworkCase import RiverNetwork
import pandas as pd
import time

river_data = 'data_gloric/padma_gloric_1m3_final_no_geo.pkl'
watersheds_data = 'data_gloric/areas_gloric_no_geo.pkl'
rain_data = 'data_pmm/20130616-S000000-E002959-20130617-S233000-E235959.pkl'
result_data = 'data_results/overflow_130616_130617_2.pkl'

padma = pd.read_pickle(river_data)
padma = padma.set_index('Reach_ID',drop=False)
padma.head()

start = time.time()
rivernetwork = RiverNetwork(river_data, rain_data, x = 0.2, speed = 2, t_max = 2*24*60)
end = time.time()
print('Duration: {:.2f}'.format(end - start) + 's')

start = time.time()
rivernetwork.calculate_flows()
end = time.time()
print('Duration: {:.2f}'.format(end - start) + 's')

overflow = rivernetwork.get_overflow()

overflow.to_pickle(result_data)



import pickle
f = open("data_results/raw_object_130616_130617_2.pkl","wb")
pickle.dump(rivernetwork,f)
f.close()





for node_str in rivernetwork.G.nodes:
    node = rivernetwork.G.nodes[node_str]
    if node['source'] == True:
        #print(node);
        break;

rivernetwork.plot_node_flows(node_str)

rivernetwork.plot_node_flows(node_str)

len(rivernetwork.get_node(50000000)['Qout'])

rivernetwork.plot_node_flows(50000000)

rivernetwork.plot_node_flows(50000001)

rivernetwork.plot_node_flows(40641811)



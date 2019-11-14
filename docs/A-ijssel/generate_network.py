#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import networkx as nx

def get_network():
    ''' Build network uploading crucial parameters '''
    
    # load data
    df = pd.read_excel('../../data/network-structure.xlsx')
    df = df.set_index('node')
    nodes = df.to_dict('index')

    # create network
    G = nx.DiGraph()
    for key, attr in nodes.items():
        G.add_node(key, **attr)

    dike_list = df['type'][df['type'] == 'dike'].index.values

    # load muskingum parameters
    Muskingum_params = pd.read_excel('../../data/params.xlsx',
                                     index_col=0)
    
    # assign parameters to nodes
    for dike in dike_list:
        # Assign Muskingum paramters:
        G.node[dike]['C1'] = Muskingum_params.loc[G.node[dike]['pnode'], 'C1']
        G.node[dike]['C2'] = Muskingum_params.loc[G.node[dike]['pnode'], 'C2']
        G.node[dike]['C3'] = Muskingum_params.loc[G.node[dike]['pnode'], 'C3']

    # assign wave shapes to first node
    G.node['A.0']['Qevents_shape'] = pd.read_excel(
            '../../data/wave_shapes.xls', index_col=0)

    return G, dike_list

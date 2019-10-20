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

import sys
import os
cwd = os.getcwd()
os.chdir(os.path.join(cwd,'..'))
sys.path.append(os.path.join(cwd,'..'))

import numpy as np
import matplotlib.pyplot as plt
import generate_network
import pandas as pd
from functions_ijssel_muskingum import Muskingum

G, dike_list = generate_network.get_network()


class DikeNetwork(object):
    def __init__(self):
        # planning steps
        self.num_events = 30
        
        # load network
        G, dike_list = generate_network.get_network()

        self.Qpeaks = 2000 #np.random.uniform(1000,16000,100)
        
        self.G = G
        self.dikelist = dike_list
        
    def printG(self):
        print(G.nodes.data())
        
    def getG(self):
        return G
        
        
    def init_node(self,value, time):
        init = np.repeat(value, len(time)).tolist()
        return init

    def _initialize_hydroloads(self, node, time, Q_0):
        #node['cumVol'], node['wl'], node['Qpol'], node['hbas'] = (
        #    self.init_node(0, time) for _ in range(4))
        node['Qin'], node['Qout'] = (self.init_node(Q_0, time) for _ in range(2))
        #node['status'] = self.init_node(False, time)
        #node['tbreach'] = np.nan
        return node
    
    def calc_wave(self,timestep=1):
        startnode = G.node['A.0']
        waveshape_id = 0
        Qpeak = self.Qpeaks#[0]
        dikelist = self.dikelist
        time = np.arange(0, startnode['Qevents_shape'].loc[waveshape_id].shape[0],
                             timestep)
        startnode['Qout'] = Qpeak * startnode['Qevents_shape'].loc[waveshape_id]
        
        # Initialize hydrological event:
        for key in dikelist:
            node = G.node[key] 
            #Q_0 = int(G.node['A.0']['Qout'][0])
            Q_0 = G.node['A.0']['Qout'][0]
            self._initialize_hydroloads(node, time, Q_0)
            
        # Run the simulation:
        # Run over the discharge wave:
        for t in range(1, len(time)):
            # Run over each node of the branch:
            for n in range(0, len(dikelist)):
                # Select current node:
                node = G.node[dikelist[n]]
                if node['type'] == 'dike':
                    # Muskingum parameters:
                    C1 = node['C1']
                    C2 = node['C2']
                    C3 = node['C3']
                    
                    prev_node = G.node[node['pnode']]
                    # Evaluate Q coming in a given node at time t:
                    node['Qin'][t] = Muskingum(C1, C2, C3,
                                                   prev_node['Qout'][t],
                                                   prev_node['Qout'][t - 1],
                                                   node['Qin'][t - 1])
                     
                    node['Qout'][t] = node['Qin'][t]
                    
    def __call__(self, timestep=1, **kwargs):
        G = self.G
        Qpeaks = self.Qpeaks
        dikelist = self.dikelist

dikeNetwork = DikeNetwork()

dikeNetwork.calc_wave()

G = dikeNetwork.getG()

# +
#G.nodes['A.1']

# +
plt.figure(figsize=(20,10))
plt.plot(G.node['A.0']['Qout'])
df = pd.DataFrame({'Qin':G.node['A.0']['Qout']})

dikelist = dikeNetwork.dikelist
for n in range(0, len(dikelist)):
    node = G.node[dikelist[n]]
    plt.plot(node['Qin'])
    df[dikelist[n]] = node['Qin']
# -

df

G.node['A.0']['Qout'][0]

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

# +
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fit_muskingum import getParams
from fit_muskingum import calc_Out
from fit_muskingum import calc_C

import generate_network
# -

G, dike_list = generate_network.get_network()

for x in dike_list:
    print(G.node[x])

G.node['A.0']['Qout'] = 2000 * G.node['A.0']['Qevents_shape'].loc[0]

Qin = 2000 * G.node['A.0']['Qevents_shape'].loc[0]

df = pd.DataFrame({'Qin':Qin})

# +
x = -1.055501123
k = 0.378929169
dt = 1

C1 = calc_C(k,x,dt)
QA1 = calc_Out(Qin,C1)
#df['A.1test'] = QA1
# -

params = pd.read_excel('./data/params.xlsx',index_col=0)
params

params.loc['A.0']['K']

# +
Qin = 2000 * G.node['A.0']['Qevents_shape'].loc[0]

nodes = ['A.0','A.1','A.2','A.3','A.4']
nodes_title = ['A.1','A.2','A.3','A.4','A.5']
i=0
for node in nodes:
    k = params.loc[node]['K']
    x = params.loc[node]['X']
    dt = 1
    C = calc_C(k,x,dt)
    Qin = calc_Out(Qin,C)
    df[nodes_title[i]] = Qin
    i = i+1
# -

df

df.plot(figsize=(20,10))

# +
# #%qtconsole

# +
fig = plt.figure(figsize=(3,2.3),dpi=150)

ax = fig.add_subplot(111)
for axis in ['top','bottom','left','right']:
    ax.spines[axis].set_linewidth(0.5)

#plt.plot(t,I,linewidth = 1 , label = 'inflow')
df.plot(ax=ax, linewidth = 0.7)
plt.rcParams.update({'font.size': 8, 'pgf.rcfonts' : False})


plt.ylabel('Flow, $Q$ [m$^3$/s]')
plt.xlabel('Time [h]')
plt.legend()
# save to file
plt.savefig('../thesis/report/figs/ijssel.pdf', bbox_inches = 'tight')
plt.savefig('../thesis/report/figs/ijssel.pgf', bbox_inches = 'tight')
# -



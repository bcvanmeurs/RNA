# -*- coding: utf-8 -*-
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

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fit_muskingum import getParams
from fit_muskingum import calc_Out
from fit_muskingum import calc_C

# +
# #%qtconsole
# -

df = pd.read_excel('./data/example-inflow-karahan-adjusted.xlsx')
df = df.set_index('Time')

# K>∆t>2KX

# +
t = df.index.values
I = np.array(df['Inflow'])
fig = plt.figure(figsize=(5,2),dpi=150)

ax = fig.add_subplot(111)
for axis in ['top','bottom','left','right']:
    ax.spines[axis].set_linewidth(0.5)

plt.plot(t,I,linewidth = 1 , label = 'inflow')
plt.rcParams.update({'font.size': 8, 'pgf.rcfonts' : False})

x = 0.2
k = 2
dt = 1

C0 = calc_C(k,x,dt) # k,x,dt
O0 = calc_Out(I,C0)
plt.plot(t, O0 ,'g',linewidth = 1, label = 'outflow')

plt.ylabel('Flow, $Q$ [m$^3$/s]')
plt.xlabel('Time [h]')
plt.legend()
# save to file
#plt.savefig('../thesis/report/figs/1reach.pdf', bbox_inches = 'tight')
plt.savefig('../thesis/report/figs/1reach.pgf', bbox_inches = 'tight')

# +
t = df.index.values
I = np.array(df['Inflow'])

length = 50
t = range(0,length,1)
I = np.append(I,np.full((1,length - len(I)),22))

fig = plt.figure(figsize=(5,2.5),dpi=150)
ax = fig.add_subplot(111)
for axis in ['top','bottom','left','right']:
    ax.spines[axis].set_linewidth(0.5)
plt.rcParams.update({'font.size': 8, 'pgf.rcfonts' : False})
    
plt.plot(t,I,linewidth = 1 , label = 'inflow')

klist = [1,3,5,10,25,50]
for k in klist:
    x = 0.01
    dt = 1 
    out = calc_Out(I,calc_C(k,x,dt))
    plt.plot(t, out,linewidth = 1, label = 'outflow $k$ = ' + '{:02d}'.format(k)) 
    
plt.ylabel('Flow, $Q$ [m$^3$/s]')
plt.xlabel('Time [h]')
plt.legend()
# save to file
#plt.savefig('../thesis/report/figs/1reachk.pdf', bbox_inches = 'tight')
plt.savefig('../thesis/report/figs/1reachk.pgf', bbox_inches = 'tight')

# +
t = df.index.values
I = np.array(df['Inflow'])

fig = plt.figure(figsize=(5,2.5),dpi=150)
ax = fig.add_subplot(111)
for axis in ['top','bottom','left','right']:
    ax.spines[axis].set_linewidth(0.5)
plt.rcParams.update({'font.size': 8, 'pgf.rcfonts' : False})
    
plt.plot(t,I,linewidth = 1 , label = 'inflow')
    
for x in [0,0.25,0.5]:
    k = 1
    dt = 1
    out = calc_Out(I,calc_C(k,x,dt))
    plt.plot(t, out,linewidth = 1, label = 'outflow $x$ = ' + '{:01.1f}'.format(x))    

    
plt.ylabel('Flow, $Q$ [m$^3$/s]')
plt.xlabel('Time [h]')
plt.legend()
# save to file
#plt.savefig('../thesis/report/figs/1reachx.pdf', bbox_inches = 'tight')
plt.savefig('../thesis/report/figs/1reachx.pgf', bbox_inches = 'tight')
plt.xlim(2,20)
# -



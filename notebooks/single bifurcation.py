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
import seaborn as sns
from fit_muskingum import getParams
from fit_muskingum import calc_Out
from fit_muskingum import calc_C

# +
# #%qtconsole
# -

df = pd.read_excel('./data/example-inflow-karahan-adjusted.xlsx')
df = df.set_index('Time')

df.plot()

# K>∆t>2KX

# +
t = df.index.values
I = np.array(df['Inflow'])

frac = 0.4
I1 = np.array(df['Inflow'])*frac
I2 = np.array(df['Inflow'])*(1-frac)
fig = plt.figure(figsize=(5,2),dpi=150)

ax = fig.add_subplot(111)
for axis in ['top','bottom','left','right']:
    ax.spines[axis].set_linewidth(0.5)
plt.rcParams.update({'font.size': 8, 'pgf.rcfonts' : False})

plt.plot(t,I,linewidth = 1 , label = 'outflow before bifurcation')

plt.plot(t,I1,linewidth = 1 , label = 'inflow 1 after bifurcation $f=0.4$')
plt.plot(t,I2,linewidth = 1 , label = 'inflow 2 after bifurcation $f=0.6$')

x = 0.1
k = 5
dt = 1
C1 = calc_C(k,x,dt) # k,x,dt
O1 = calc_Out(I1,C1)
plt.plot(t, O1 ,'r',linewidth = 1, label = 'outflow 1, $x=0.1$, $k=5$')

x = 0.2
k = 2
dt = 1
C2 = calc_C(k,x,dt) # k,x,dt
O2 = calc_Out(I2,C2)
plt.plot(t, O2 ,linewidth = 1, label = 'outflow 2, $x=0.2$, $k=2$')

plt.ylabel('Flow, $Q$ [m$^3$/s]')
plt.xlabel('Time [h]')
plt.legend()
# save to file
#plt.savefig('../thesis/report/figs/1bifurcation.pdf', bbox_inches = 'tight')
plt.savefig('../thesis/report/figs/1bifurcation.pgf', bbox_inches = 'tight')
# -



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
I2 = np.array(df['Inflow'])*0.4
I2 = np.append(I2[28:37],I2[0:28])
fig = plt.figure(figsize=(5,2),dpi=150)

ax = fig.add_subplot(111)
for axis in ['top','bottom','left','right']:
    ax.spines[axis].set_linewidth(0.5)

plt.plot(t,I,'--',linewidth = 1 , label = 'outflow 1')
plt.plot(t,I2,'--',linewidth = 1 , label = 'outflow 2')
plt.plot(t,I+I2,linewidth = 1 , label = 'inflow')
plt.rcParams.update({'font.size': 8, 'pgf.rcfonts' : False})

x = 0.1
k = 5
dt = 1

C0 = calc_C(k,x,dt) # k,x,dt
O0 = calc_Out(I+I2,C0)
plt.plot(t, O0 ,'r',linewidth = 1, label = 'outflow')

plt.ylabel('Flow, $Q$ [m$^3$/s]')
plt.xlabel('Time [h]')
plt.legend()
# save to file
plt.savefig('../thesis/report/figs/1confluence.pdf', bbox_inches = 'tight')
plt.savefig('../thesis/report/figs/1confluence.pgf', bbox_inches = 'tight')

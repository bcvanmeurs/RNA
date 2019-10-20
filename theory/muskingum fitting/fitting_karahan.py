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

df = pd.read_excel('./data/example-inflow-karahan.xlsx')
df = df.set_index('Time')

t = df.index.values
I = np.array(df['Inflow'])
O = np.array(df['Outflow'])

# +
plt.plot(t,I)
plt.plot(t,O)

# x = 0.221, k = 29.165 hours, dt = 6 hours
x = 0.221
k = 29.165
dt = 6

C0 = calc_C(k,x,dt) # k,x,dt
O_paper = calc_Out(I,C0)
df['karahan'] = O_paper
plt.plot(t, O_paper ,'gx')
# -

params = getParams(I,O,6)
params

# +
C_est = calc_C(params['k'],params['x'],6)
O_est = calc_Out(I,C_est)

plt.plot(t,I)
plt.plot(t,O)
plt.plot(t,O_paper,'g--')
plt.plot(t,O_est,'rx')
df['estimated'] = O_est
# -



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

df = pd.read_excel('./data/example-inflow.xlsx')
df = df.set_index('Time')

t = df.index.values
I = np.array(df['Inflow'])
O = np.array(df['Outflow'])

# +
plt.plot(t,I)
plt.plot(t,O)

# x = 0.15, k = 2.3 hours, dt = 1 hour
x = 0.15
k = 2.3
dt = 1

C0 = calc_C(k,x,dt)
O_paper = calc_Out(I,C0)
df['colorado'] = O_paper
plt.plot(t, O_paper ,'gx')
# -

params = getParams(I,O,dt)
params

# +
C_est = calc_C(params['k'],params['x'],dt)
O_est = calc_Out(I,C_est)

plt.plot(t,I)
plt.plot(t,O)
plt.plot(t,O_paper,'g--')
plt.plot(t,O_est,'rx')
df['estimated'] = O_est
# -

k*(x*I+(1-x)*O)

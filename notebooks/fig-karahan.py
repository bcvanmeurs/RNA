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

# # Fig karahan

# In this notebook the model is verified by comparing outcomes of two different examples.

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from context import RiverNetwork
from RiverNetwork import RiverNetwork

# %load_ext autoreload
# %autoreload 2

# In this example the Wilson dataset from the Karahan paper is used.
# Karahan compared different estimation techniques.
# It is a simple one segment model.
# The most interesting difference here is that $\Delta t$ is not 1 but karahan uses a value of 6.
# For this dataset the $x$ is estimated on 0.021 and $k$ to 29.165.
# This can also be seen in the figure.
# The base load is set to 22.

# https://onlinelibrary.wiley.com/doi/full/10.1002/cae.20394

# ### Loading data

structure2 = RiverNetwork('../data/single-segment-karahan.xlsx',dt=6)
structure2.draw(figsize=(3,2.5))

inflow = np.array(pd.read_excel('../data/example-inflow-karahan.xlsx').Inflow)
structure2.set_shape('S.1',21,inflow-22)
structure2.draw_Qin(only_sources=True,figsize=(7,4))

# ### Results of flow propagation

# The flow is calculated for the sink node.

structure2.calc_flow_propagation(22)
plt.rcParams.update({'font.size': 8, 'pgf.rcfonts' : False})
structure2.draw_Qin(figsize=(5,2))
#plt.savefig('../../thesis/report/figs/karahan.pgf', bbox_inches = 'tight')
#plt.savefig('../../thesis/report/figs/karahan.pdf', bbox_inches = 'tight')

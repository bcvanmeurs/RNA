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

# # Calculation order

# This simple network only contains confluences and no bifurcations.

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from context import RiverNetwork
from RiverNetwork import RiverNetwork

# ## Loading network structure

# An extra file containing wave shapes is loaded as well.
# This file makes it possible to select arbitrary wave shapes as input flows.

structure1 = RiverNetwork('../data/calculation-order.xlsx',wave_shapes_location='../data/wave_shapes.xls')

structure1.draw(labels=False)
#plt.savefig('../../thesis/report/figs/calculation-order.pdf', bbox_inches = 'tight')



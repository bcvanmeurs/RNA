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

# # Single bifurcation

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# %load_ext autoreload
# %autoreload 2

from RiverNetwork import RiverNetwork

structure1 = RiverNetwork('data/single-bifurcation.xlsx',wave_shapes_location='data/wave_shapes.xls')
structure1.draw()

structure1.draw_base_loads()

inflow = np.array(pd.read_excel('./data/example-inflow-karahan-adjusted.xlsx').Inflow)-22

structure1.set_shape('S.1',30,inflow)
structure1.draw_Qin(True)

structure1.calc_flow_propagation(30)

structure1.draw_Qin()



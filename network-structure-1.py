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

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# %load_ext autoreload
# %autoreload 2

from RiverNetwork import RiverNetwork

structure1 = RiverNetwork('data/network-structure-1.xlsx')

structure1.draw()

structure1.draw_base_loads()

#structure1.set_constant_flow('S.1',30)
shape = np.zeros(30)
shape[4] = 1
shape[5] = 3
shape[6] = 10
shape[7] = 3
shape[8] = 1
structure1.set_shape('S.1',30,shape)
structure1.set_wave('S.2',shape_number=5,strength=5)
#structure1.set_constant_flow('S.3',30)
structure1.set_wave('S.3',shape_number=90,strength=5)
structure1.set_constant_flow('S.4',30)
structure1.draw_Qin(True)

structure1.calc_flow_propagation(30)

structure1.draw_Qin()

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

import numpy as np
from RiverNetwork import RiverNetwork
from ipysheet import from_dataframe
import ipysheet

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# %load_ext autoreload
# %autoreload 2

df = pd.read_excel('data/network-structure-1.xlsx')
df

sheet = from_dataframe(df)
display(sheet)

ipysheet.pandas_loader.to_dataframe(sheet)



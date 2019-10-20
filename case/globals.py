import numpy as np

def bounds(margin = 0):
    return np.array([73.94375 - margin   , 22.55208333 - margin, 97.73958333 + margin , 31.38541667 + margin])

def dates():
    dates = ['2013/06/' + str(day) for day in range(14,21)]
    return dates
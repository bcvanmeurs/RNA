import numpy as np
import math
from scipy.optimize import minimize

def calc_C(k,x,dt):
    C0 = dt/k+2*(1-x)
    C1 = ((dt/k)-2*x)/C0
    C2 = ((dt/k)+2*x)/C0
    C3 = (2*(1-x)-dt/k)/C0
    return {'0':C0 ,'C1':C1 ,'C2':C2, 'C3':C3, 'dt':dt}

def calc_C_auto_dt(k,x):
    dt = math.ceil(2 * k * x)
    C0 = dt/k+2*(1-x)
    C1 = ((dt/k)-2*x)/C0
    C2 = ((dt/k)+2*x)/C0
    C3 = (2*(1-x)-dt/k)/C0
    return {'0':C0 ,'C1':C1 ,'C2':C2, 'C3':C3, 'dt':dt}

def calc_C_karahan(k,x,dt):
    C1 = (0.5*dt-k*x)/((1-x)*k+0.5*dt)
    C2 = (k*x+0.5*dt)/((1-x)*k+0.5*dt)
    C3 = (-0.5*dt+(1-x)*k)/((1-x)*k+0.5*dt)
    return {'C1':C1 ,'C2':C2, 'C3':C3}

def calc_Out(I,C,I0=True):
    Out = np.zeros(I.shape)
    if I0 == True:
        Out[0] = I[0]
    else:
        Out[0]= I0
    
    for i in range(1,len(I)):
        Out[i] = I[i]*C['C1'] + I[i-1]*C['C2'] + Out[i-1]*C['C3']
    return Out

def difference(x,*flow):
    I = flow[0]
    O = flow[1]
    dt = flow[2]
    C = calc_C(x[0],x[1],dt)
    O_est = calc_Out(I,C)
    return sum((O_est - O)**2)

def getParams(I,O,dt):
    flow = (I,O,dt)
    x0 = np.array([1 ,1])
    res = minimize(difference, x0, args=flow, method='nelder-mead', options={'xtol': 1e-10, 'disp': False})
    return {'k':res.x[0],'x':res.x[1]}
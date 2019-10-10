import geopandas as gp
import pandas as pd
import networkx as nx
import numpy as np

class RiverNetwork:
    def __init__(self, river_data, watershed_data,rain_data, x, speed, delta_t = 30, t_max = 1440):
        padma = pd.read_pickle(river_data)
        watersheds = pd.read_pickle(watershed_data)
        rain = pd.read_pickle(rain_data)
        self.x = x
        self.speed = speed
        self.time = time = np.arange(0,t_max,delta_t)
        self.delta_t = delta_t
        self.L_max = delta_t * 60 * speed / (2 * x) / 1000
        self.L_min = delta_t * 60 * speed / (2 * (1-x)) / 1000
        self.runoff_coeff

        G = nx.DiGraph()
        G.add_nodes_from(padma['Reach_ID'])

        # add edges to graphs
        for index,row in padma[['Reach_ID','Next_down']].iterrows():
            G.add_edge(row['Reach_ID'],row['Next_down'])

        self.G = G

        # add data to nodes
        for index,row in padma.iterrows():
            length = row['Length_km']
            G.nodes[row['Reach_ID']]['Length_km'] = length
            G.nodes[row['Reach_ID']]['Log_Q_avg'] = row['Log_Q_avg']
            G.nodes[row['Reach_ID']]['Log_Q_var'] = row['Log_Q_var']
            if (length < self.L_max) & (length > self.L_min):
                G.nodes[row['Reach_ID']]['split'] = 1
            if length > self.L_max:
                G.nodes[row['Reach_ID']]['split'] = int(length // self.L_max + 1) 
            if length < self.L_min:
                G.nodes[row['Reach_ID']]['split'] = -int(self.L_min // length +1) 
            G.nodes[row['Reach_ID']]['C'] = calc_C(self.x, length * 1000, self.speed, self.delta_t) 
            
            if len(list(G.predecessors(row['Reach_ID']))) == 0:
                G.nodes[row['Reach_ID']]['source'] = True
                G.nodes[row['Reach_ID']]['Qin'] =  np.full(t_max//delta_t,10**row['Log_Q_avg'])
            else:
                G.nodes[row['Reach_ID']]['source'] = False
                G.nodes[row['Reach_ID']]['Qin'] =  np.concatenate(( [10**row['Log_Q_avg']], np.zeros(t_max//delta_t) ))
            G.nodes[row['Reach_ID']]['Qout'] = np.concatenate(( [10**row['Log_Q_avg']], np.zeros(t_max//delta_t) ))
        
        # add rainfall data to nodes
        for index,row in rain.iterrows(): #rain.iterrows():
            G.nodes[row['Reach_ID']]['area_sk'] = row['area_sk']
            G.nodes[row['Reach_ID']]['net_inflow'] = self.get_net_inflow(row['Reach_ID'])
            G.nodes[row['Reach_ID']]['rain'] = row.drop(labels={'Reach_ID','area_sk'}).to_numpy()

        self.calculation_order = list(reversed(list(nx.edge_bfs(G,0,'reverse'))))
        self.G = G
    
    def get_outflow(self, Reach_ID, t):
        node = self.G.nodes[Reach_ID]
        C = node['C']

        # inflow consist of (on both t and t-1)
        #       - previous node
        #       - static inflow
        #       - rain
        
        if node['source'] == True:
            # No previous node inflow

            # rain is in mm/hour
            # area is in square km
            # convert to cubic meters per half hour
            Q_rain = node['rain'] * node['area_sk'] * 1e3 * 0.5 * self.runoff_coeff
            Q_static = node['net_inflow']
            Qin = Q_rain + Q_static

            
            
            node['Qout'][t] = node['Qin'][t]*C['C1'] + node['Qin'][t-1]*C['C2'] + node['Qout'][t-1]*C['C3']



    def get_net_inflow(self,Reach_ID):
        total_inflow = 0
        G = self.G
        for predecessor in G.predecessors(Reach_ID):
            total_inflow = total_inflow + (10 ** G.nodes[predecessor]['Log_Q_avg'])
        net_inflow = (10 ** G.nodes[Reach_ID]['Log_Q_avg']) - total_inflow
        return net_inflow

    def get_node(self,Reach_ID):
        return self.G.nodes[Reach_ID]
    

def calc_C(x,L,speed,dt):
    dt = dt*60
    k = L / speed
    C0 = dt/k+2*(1-x)
    C1 = ((dt/k)-2*x)/C0
    C2 = ((dt/k)+2*x)/C0
    C3 = (2*(1-x)-dt/k)/C0
    return {'0':C0 ,'C1':C1 ,'C2':C2, 'C3':C3, 'dt':dt/60}
import geopandas as gp
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()

class RiverNetwork:
    def __init__(self, river_data, watershed_data,rain_data, x, speed, runoff_coeff = 0.5 , delta_t = 30, t_max = 1440):
        if isinstance(river_data,str):
            padma = pd.read_pickle(river_data)
        elif isinstance(river_data,pd.DataFrame): 
            padma = river_data
        
        # if isinstance(watershed_data,str):
        #     watersheds = pd.read_pickle(watershed_data)
        # elif isinstance(watershed_data,pd.DataFrame): 
        #     watersheds = watershed_data
        
        if isinstance(rain_data,str):
            rain = pd.read_pickle(rain_data)
        elif isinstance(rain_data,pd.DataFrame): 
            rain = rain_data
        rain = rain.set_index('Reach_ID',drop=False)
         
        self.x = x
        self.speed = speed
        self.time = time = np.arange(0,t_max,delta_t)
        self.t_max = t_max
        self.delta_t = delta_t
        # in km
        self.L_max = delta_t * 60 * speed / (2 * x) / 1000
        self.L_min = delta_t * 60 * speed / (2 * (1-x)) / 1000
        self.runoff_coeff = runoff_coeff

        padma_original = padma.copy()
        padma = split_reaches(padma,self.L_max)

        # should check if ids in files match!
        # set sink node

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
            G.nodes[row['Reach_ID']]['Q_avg']     = 10**row['Log_Q_avg']
            G.nodes[row['Reach_ID']]['Q_max']     = 10**row['Log_Q_avg'] * 10**row['Log_Q_var']
            G.nodes[row['Reach_ID']]['Log_Q_var'] = row['Log_Q_var']
            if (length <= self.L_max) & (length >= self.L_min):
                G.nodes[row['Reach_ID']]['split'] = 0
                G.nodes[row['Reach_ID']]['C'] = calc_C(self.x, length * 1000, self.speed, self.delta_t) 
            if row['Splits'] > 1:
                G.nodes[row['Reach_ID']]['split'] = row['Splits']
                G.nodes[row['Reach_ID']]['C'] = calc_C(self.x, length * 1000, self.speed, self.delta_t) 
            if length < self.L_min:
                G.nodes[row['Reach_ID']]['split'] = -int(self.L_min // length +1) 
                sub_timestamps = abs(G.nodes[row['Reach_ID']]['split'])
                while not (self.delta_t % sub_timestamps == 0) :
                    sub_timestamps += 1
                G.nodes[row['Reach_ID']]['C'] = calc_C(self.x, length * 1000, self.speed, self.delta_t/sub_timestamps) 
                G.nodes[row['Reach_ID']]['sub_timestamps'] = sub_timestamps
            if len(list(G.predecessors(row['Reach_ID']))) == 0:
                G.nodes[row['Reach_ID']]['source'] = True
            else:
                G.nodes[row['Reach_ID']]['source'] = False
            G.nodes[row['Reach_ID']]['Qin'] = np.zeros(t_max//delta_t )
            G.nodes[row['Reach_ID']]['Qout'] = np.zeros(t_max//delta_t )
            G.nodes[row['Reach_ID']]['Qover'] = np.zeros(t_max//delta_t )
        
        # add rainfall data to nodes
            # preferably this loop is merged with the above one, but get_static_inflow needs flows from predecessors, the might not be set.
        for index, row in padma.iterrows():
            Reach_ID    = row['Reach_ID']
            Original_ID = row['Original_ID']
            G.nodes[Reach_ID]['Original_ID']        = Original_ID
            G.nodes[Reach_ID]['area_sk']            = rain.loc[Original_ID]['area_sk'] / row['Splits']
            G.nodes[Reach_ID]['static_inflow']      = self.get_static_inflow(Reach_ID)
            G.nodes[Reach_ID]['rain']               = rain.loc[Original_ID].drop(labels={'Reach_ID','area_sk'}).to_numpy()

        self.calculation_order = list(reversed(list(nx.edge_bfs(G,0,'reverse'))))
        G.remove_node(0) # remove virtual sink node
        self.G = G
    
    def set_zero_loads(self):
        for Reach_ID, y, z in self.calculation_order:
            self.set_outflow(Reach_ID,0)

    def calculate_flows(self):
        for t in np.arange(self.t_max//self.delta_t):
            for Reach_ID, y, z in self.calculation_order:
                self.set_outflow(Reach_ID,t)


    def set_outflow(self, Reach_ID, t):
        node = self.G.nodes[Reach_ID]
        if node['split'] == 0:
            self.set_outflow_nosplit(Reach_ID, node, t)
        elif node['split'] < -1:
            self.set_outflow_sub_timestamp(Reach_ID, node, t)
        elif node['split'] > 1:
            self.set_outflow_nosplit(Reach_ID, node, t)
        
    def set_outflow_nosplit(self, Reach_ID, node, t):
        C = node['C']
        # rain is in mm/hour
        # area is in square km
        # convert to cubic meters per half hour

        Q_rain = node['rain'][t] * node['area_sk'] * 1e3 / 3600 * self.runoff_coeff
        Q_static = node['static_inflow']

        if node['source'] == True:
            # No previous node inflow
            Qin = Q_rain + Q_static
        
        else: # if not source node
            Q_predecessor = self.get_outflow_predecessors(Reach_ID,t)
            Qin = Q_rain + Q_static + Q_predecessor

        node['Qin'][t] = Qin
        if t == 0:
            node['Qout'][t] = Qin
        else:
            node['Qout'][t] = node['Qin'][t]*C['C1'] + node['Qin'][t-1]*C['C2'] + node['Qout'][t-1]*C['C3']
        node['Qover'][t] =  max(node['Qout'][t] - node['Q_max'],0)
    
    def set_outflow_sub_timestamp(self, Reach_ID, node, t):
        C = node['C']
        sub_timestamps = node['sub_timestamps']
                
        Q_rain = node['rain'][t] * node['area_sk'] * 1e3 / 3600 * self.runoff_coeff
        Q_static = node['static_inflow']

        if t == 0:
            if node['source'] == True:
                Qin = Q_rain + Q_static 
            else:
                Q_predecessor = self.get_outflow_predecessors(Reach_ID,t)
                Qin = Q_rain + Q_static + Q_predecessor
            node['Qin'][t] = Qin
            node['Qout'][t] = Qin
        else:
            Qin_sub     = np.zeros(sub_timestamps + 1)
            Qin_sub[0]  = node['Qin'][t-1]
            Qout_sub    = np.zeros(sub_timestamps + 1)
            Qout_sub[0] = node['Qout'][t-1]
            #print(Qin_sub)
            #print(Qout_sub)

            if node['source'] == True:
                for sub_timestamp in np.arange(1 , sub_timestamps + 1):
                    Qin = Q_rain + Q_static 
                    Qin_sub[sub_timestamp] = Qin
                    Qout_sub[sub_timestamp] = Qin_sub[sub_timestamp]*C['C1'] + Qin_sub[sub_timestamp-1]*C['C2'] + Qout_sub[sub_timestamp-1]*C['C3']
            else:
                for sub_timestamp in np.arange(1 , sub_timestamps + 1):
                    Q_predecessor = self.get_outflow_predecessors(Reach_ID,t,split=node['split'], sub_timestamp=sub_timestamp)
                    #print(Q_predecessor)
                    Qin = Q_rain + Q_static + Q_predecessor
                    Qin_sub[sub_timestamp] = Qin
                    Qout_sub[sub_timestamp] = Qin_sub[sub_timestamp]*C['C1'] + Qin_sub[sub_timestamp-1]*C['C2'] + Qout_sub[sub_timestamp-1]*C['C3']
            #print(Qin_sub)
            #print(Qout_sub)
            node['Qin'][t]  = Qin_sub[-1]
            node['Qout'][t] = Qout_sub[-1]
        node['Qover'][t] =  max(node['Qout'][t] - node['Q_max'],0)
            
    def get_outflow_predecessors(self,Reach_ID,t,split = 0, sub_timestamp = 0):
        G = self.G

        if split >= 0:
            total_outflow = 0
            for predecessor in G.predecessors(Reach_ID):
                total_outflow = total_outflow + G.nodes[predecessor]['Qout'][t]
            return total_outflow
        elif split < -1:
            sub_timestamps = G.nodes[Reach_ID]['sub_timestamps']
            x = np.arange(2)
            result_x = np.linspace(0,1,sub_timestamps+1)

            #print(x)
            #print(result_x)

            total_outflow = np.zeros((len(list(G.predecessors(Reach_ID))),2))
            #total_outflow_new = list()
            total_outflow_at_sub = 0
            i = 0
            for predecessor in G.predecessors(Reach_ID):
                total_outflow[i][0] =  G.nodes[predecessor]['Qout'][t-1]
                total_outflow[i][1] =  G.nodes[predecessor]['Qout'][t]
                
                #print(total_outflow[i])

                #total_outflow_new.append( np.interp(result_x,x,total_outflow[i]) )
                total_outflow_at_sub +=  np.interp(result_x,x,total_outflow[i])[sub_timestamp] 
                i = i + 1
            #print(total_outflow_new)
        return total_outflow_at_sub 

    def get_static_inflow(self,Reach_ID):
        total_inflow = 0
        G = self.G
        for predecessor in G.predecessors(Reach_ID):
            total_inflow = total_inflow + (10 ** G.nodes[predecessor]['Log_Q_avg'])
        static_inflow = (10 ** G.nodes[Reach_ID]['Log_Q_avg']) - total_inflow
        return static_inflow

    def get_node(self,Reach_ID):
        return self.G.nodes[Reach_ID]
    
    def plot_node_flows(self,Reach_ID):
        node = self.G.nodes[Reach_ID]
        Qin = node['Qin']
        Qout = node['Qout']
        Q_rain = node['rain'] * node['area_sk'] * 1e3 / 3600 * self.runoff_coeff
        time = np.arange(0,self.t_max/30/2,0.5)
        fig, ax = plt.subplots()
        fig.patch.set_alpha(0)
        sns.lineplot(time, Qin, label='Inflow')
        sns.lineplot(time, Qout, label='Outflow')
        sns.lineplot(time, Q_rain[0:len(time)], label='Rain')
        sns.lineplot(time, np.full(len(time),node['Q_avg']),label='Average flow')
        sns.lineplot(time, np.full(len(time),node['Q_max']),label='Maximum flow')
        plt.fill_between(time,node['Q_max'],Qout, where=Qout>=node['Q_max'],label = 'Overflow', color = 'r', alpha=0.2)
        plt.xlabel('Time [h]')
        plt.ylabel('Discharge [m$^3$/s]')
        plt.title('Discharge graph of node: ' + str(Reach_ID))
        plt.legend()
        return(fig,ax)

    def get_overflow(self):
        data = {}
        for Reach_ID in self.G.nodes:
            node = self.G.node[Reach_ID]
            Qover = node['Qover']
            data[Reach_ID] = {**{i: el for i, el in enumerate(Qover)}, **{'Original_ID':node['Original_ID']}}
        data = pd.DataFrame.from_dict( data , orient='index' ).astype({'Original_ID':int})
        data = data.rename_axis('Reach_ID')
        data = data.reset_index().\
            sort_values(by=['Reach_ID','Original_ID']).\
            drop_duplicates(subset='Original_ID', keep='last').\
            drop('Reach_ID',axis=1).\
            set_index('Original_ID').\
            rename_axis('Reach_ID')
        return data

def calc_C(x,L,speed,dt):
    dt = dt*60
    k = L / speed
    C0 = dt/k+2*(1-x)
    C1 = ((dt/k)-2*x)/C0
    C2 = ((dt/k)+2*x)/C0
    C3 = (2*(1-x)-dt/k)/C0
    return {'0':C0 ,'C1':C1 ,'C2':C2, 'C3':C3, 'dt':dt/60, 'L':L}

def split_reaches(padma,L_max):

    max_id = max(padma['Reach_ID'])
    digits = len(str(max_id))
    free_id = int(round(max_id,-digits+1) + 10**(digits-1))
    
    max_index = max(padma.index)
    free_index = int(max_index + 1)
    padma['Original_ID'] = padma['Reach_ID']
    padma['Splits'] = 1
    types = padma.dtypes
    
    for index, row in padma[padma['Length_km'] > L_max].copy().iterrows():
        length = row['Length_km']
        splits = int(length // L_max + 1)
        start_id = row['Reach_ID']
        successor_id  = row['Next_down']
        Log_Q_avg = row['Log_Q_avg']
        Log_Q_var = row['Log_Q_var']
        
        for split in np.arange(splits):
            # needs reviewing, works based on trial and error more than logic
            if split == 0:
                new_id = start_id
                next_down = free_id
            elif split == max(np.arange(splits)):
                new_id = free_id
                free_id += 1
                next_down = successor_id
            else:
                new_id = free_id
                free_id += 1
                next_down = free_id
            if split == 0:
                new_index = index
            else:
                new_index = free_index
                free_index += 1
            
            data = [new_id, next_down, length/splits, Log_Q_avg, Log_Q_var, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, start_id, splits]
            padma.at[new_index] = data
            padma = padma.astype(types)
    
    return padma

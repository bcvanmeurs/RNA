import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import numpy as np
from fit_muskingum import calc_C_auto_dt

class RiverNetwork:
    
    def __init__(self, excel_location,wave_shapes_location=None):
        # load network

        df_nodes = pd.read_excel(excel_location,sheet_name='nodes')
        df_nodes = df_nodes.astype({'source':bool,'sink':bool})
        self.df_node = df_nodes
        df_edges = pd.read_excel(excel_location,sheet_name='edges')
        self.df_edges = df_edges

        # check available columns: node, pnode, type, avg_flow, fraction
        # check if type source has no previous node
        # check if type link/sink has previous node
        # check if every node has single position and flow
        
        # Get all nodes and store as dataframe and as list
        self.nodes = list(df_nodes.node)
        sources = df_nodes[df_nodes.source]
        self.sourcenodes = list(sources.node)
        sinks = df_nodes[df_nodes.sink]
        self.sinknodes = list(sinks.node)
        
        # Get nodes and construct graph
        G = nx.DiGraph()
        G.add_nodes_from(self.nodes)
        
        # asign flow values to sources
        for index, row in sources.iterrows():
            G.nodes[row['node']]['avg_flow'] = row['avg_flow']
        
        # add edges
        for index, row in df_edges.iterrows():
            G.add_edge(row['pnode'], row['node'], weight=row['fraction'], x=row['x'], k=row['k'], C = calc_C_auto_dt(row['k'],row['x']) ) # change weigths to fractions
        
        self.G = G
        # check if all nodes are connected
        # nx.is_connected(G.to_undirected())
        # check no loops
        # nx.number_of_selfloops(G) > 0
        # sum of fractions is 1
        # check if all x and k are present
        
        
        
        # extract postions for drawing
        # what if no positions are given
        positions = df_nodes[df_nodes.draw_y.notna() & df_nodes.draw_x.notna()]
        positions = positions[['node','draw_x','draw_y']]
        coords = list(zip( 0.5*positions['draw_x'] ,  -1*positions['draw_y'] ))
        pos = dict(zip(positions.node,coords))
        self.pos = pos
        
        coords = list(zip( 0.5*positions['draw_x']+0.3 ,  -1*positions['draw_y'] ))
        self.pos_labels = dict(zip(positions.node,coords))
        
        edge_labels = {}
        for edge in G.edges:
            x = G.edges[edge[0],edge[1]]['x']
            k = G.edges[edge[0],edge[1]]['k']
            xpos = (pos[edge[1]][0] + pos[edge[0]][0])/2
            ypos = (pos[edge[1]][1] + pos[edge[0]][1])/2
            fraction = G.edges[edge[0],edge[1]]['weight']
            fraction_str = ''
            if fraction < 1:
                fraction_str =  '\nf=' + str(fraction)
            kx_string = 'k=' + str(k) + '\nx=' + str(x)  + fraction_str

            edge_labels[edge] = {'string':kx_string, 'xpos':xpos, 'ypos':ypos}
        self.edge_labels = edge_labels
    
        if wave_shapes_location:
            self.waveshapes = pd.read_excel(wave_shapes_location, index_col=0).T
        
        # Determine calculation order
        G.add_node('end')
        for sinks_str in self.sinknodes:
            G.add_edge(sinks_str,'end')
        self.calculation_order = list(reversed(list(nx.edge_bfs(G,'end','reverse'))))
        nr_edges = len(self.calculation_order)
        nr_sinks = len(self.sinknodes)
        for i in range(0,nr_sinks):
            self.calculation_order.remove(self.calculation_order[nr_edges-1-i])
        G.remove_node('end')

        self.calc_base_load()

    def set_constant_flow(self,node,steps):
        G = self.G
        G.nodes[node]['Qin'] = np.full(steps,G.nodes[node]['avg_flow'])
        G.nodes[node]['Qout'] = np.full(steps,G.nodes[node]['avg_flow']) #ugly
        
    def set_shape(self,node,steps,shape):
        G = self.G
        G.nodes[node]['Qin'] = G.nodes[node]['avg_flow'] + shape
        G.nodes[node]['Qout'] = G.nodes[node]['avg_flow'] + shape
    
    def set_wave(self,node,shape_number,strength):
        G = self.G
        wave = self.waveshapes[shape_number]
        wave = wave.subtract(wave[0])  ## wave starts at 0
        wave = wave.multiply(strength).add(G.nodes[node]['avg_flow'])
        G.nodes[node]['Qin'] = wave.to_numpy()
        G.nodes[node]['Qout'] = wave.to_numpy() #ugly
    
    def draw(self):
        options = {
            'node_color': '#1f78b4',
            #'alpha':0.5
            'node_size': 450,
            #'width': 3,
        }
        
        fig = plt.figure(figsize=(8,8))#,dpi=300)
        fig.patch.set_alpha(0)
        nx.draw(self.G, with_labels=False, pos=self.pos, **options)
        nx.draw_networkx_labels(self.G, self.pos, font_color='white' )
        
        flow_labels = nx.get_node_attributes(self.G,'avg_flow')
        nx.draw_networkx_labels(self.G, self.pos_labels, labels = flow_labels)
        
        
        
        for edge, items in self.edge_labels.items():
            t = plt.text(items['xpos'],items['ypos'],items['string']
                         ,horizontalalignment='center',verticalalignment='center')
            t.set_bbox(dict(facecolor='#fcfcfc', alpha=1,edgecolor='None'))
        
        plt.axis('equal')
        
        
    def draw_base_loads(self,timesteps = 10):
        G = self.G
        fig = plt.figure(figsize=(8,8))#,dpi=300)
        for node_str in G:
            flow = G.nodes[node_str]['avg_flow']
            t = np.arange(10)
            flow_array = np.full( 10, flow)
            fig.patch.set_alpha(0)
            sns.lineplot(t,flow_array,label=node_str)

        plt.ylabel('Flow, $Q$ [m$^3$/s]')
        plt.xlabel('Timesteps')
        plt.legend()
    
    def draw_Qin(self,only_sources=False):
        G = self.G
        fig = plt.figure(figsize=(8,8))#,dpi=300)
        if only_sources == True:
            for node_str in self.sourcenodes:
                flow = G.nodes[node_str]['Qin']
                t = np.arange(len(flow))
                fig.patch.set_alpha(0)
                sns.lineplot(t,flow,label=node_str)
        else:
            for node_str in G:
                if 'Qin' in G.nodes[node_str]:
                    flow = G.nodes[node_str]['Qin']
                    t = np.arange(len(flow))
                    fig.patch.set_alpha(0)
                    sns.lineplot(t,flow,label=node_str)
            
        plt.ylabel('Flow, $Q$ [m$^3$/s]')
        plt.xlabel('Timesteps')
        plt.legend()
        
    def draw_Qout(self):
        G = self.G
        fig = plt.figure(figsize=(8,8))#,dpi=300)
        for (node_str, successor_str, x) in self.calculation_order:
                edge = G[node_str][successor_str]
                Qin = edge['Qin']
                Qout = edge['Qout']
                t = np.arange(len(Qin))
                sns.lineplot(t,Qin,label=node_str+ ' Qin')
                sns.lineplot(t,Qout,label=node_str+ ' Qout')
                
        plt.ylabel('Flow, $Q$ [m$^3$/s]')
        plt.xlabel('Timesteps')
        plt.legend()
    
    def calc_base_load(self):
        # run max 1 time
        G = self.G
        for (node_str, successor_str, x) in self.calculation_order:
            edge = G[node_str][successor_str]
            node = G.nodes[node_str]
            successor = G.nodes[successor_str]
            flow = node['avg_flow'] * edge['weight']
            self.add_flow(successor,flow)
    
    def calc_flow_propagation(self,timesteps):
        # search for everything with 30
        G = self.G
        for node_str in G.nodes:
            if node_str not in self.sourcenodes:
                node = G.nodes[node_str]
                node['Qin'] = np.zeros(30)
                node['Qout'] = np.zeros(30)
        
        for t in np.arange(0,timesteps):
            #print(t)
            for (node_str, successor_str, x) in self.calculation_order:
                edge = G[node_str][successor_str]
                C = edge['C']
                dt = edge['C']['dt']
                node = G.nodes[node_str]
                successor = G.nodes[successor_str]
                
                if t == 0:
                    edge['Qin'] = np.zeros(30)
                    edge['Qout'] = np.zeros(30)
                    edge['Qin'][0] = node['avg_flow'] * edge['weight']
                    edge['Qout'][0] = node['avg_flow'] * edge['weight']
                    successor['Qin'][0]  = node['avg_flow'] * edge['weight'] + successor['Qin'][0]
                    successor['Qout'][0] = node['avg_flow'] * edge['weight'] + successor['Qout'][0]
                else:
                    edge['Qin'][t] = node['Qout'][t] * edge['weight']  # + external effect
                    #edge['Qout'][t] = edge['Qin'][t] # no muskingum effect
                    edge['Qout'][t] = edge['Qin'][t]*C['C1'] + edge['Qin'][t-1]*C['C2'] + edge['Qout'][t-1]*C['C3']
                    successor['Qin'][t] = edge['Qout'][t] + successor['Qin'][t]
                    successor['Qout'][t] = edge['Qout'][t] + successor['Qout'][t]
                
                #print(node_str)
                #print(successor_str)   
                #print(node)
                #print(successor)
                #print(edge)
                    
                    

    def add_flow(self,node,flow):
        if 'avg_flow' in node:
            node['avg_flow'] = node['avg_flow'] + flow
        else:
            node['avg_flow'] = flow
        
                
    def get_no_predecessors(self,node):
        return sum(1 for _ in G.predecessors(node))
        
    def get_Graph(self):
        return self.G
    
    def print_nodes(self):
        print(self.G.nodes.data())
        
    def print_arcs(self):
        print(self.G.edges.data())
        
    def get_waveshape(self,number):
        return self.waveshapes[number]
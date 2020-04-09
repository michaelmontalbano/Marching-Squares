import sys
from MarchingSquare import *
import numpy as np
import collections
import itertools
import pprint
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

class MS_Graph():
    def __init__ (self, linelist):
        self.linelist = linelist

    color= ('red','green','blue','yellow','purple','cyan','dark green','orange','greenish yellow') # figure out how to work this into the loop above   

    def getGraph(self):
        '''
        Takes self.linelist and converts to dict
        '''
        linelist = self.linelist
        # edge list usually reads v1 -> v2
        graph = {}
        # however these are lines so symmetry is assumed
        for l in linelist:
            v1, v2 = map(tuple, l)
            graph[v1] = graph.get(v1, ()) + (v2,)      
            graph[v2] = graph.get(v2, ()) + (v1,)
        return graph

    def BFS(self, graph):
        """
        Implement breadth-first search
        """
        # get nodes
        nodes = list(graph.keys())
        graphs = []
        # check all nodes 
        while nodes:
            # initialize BFS
            toCheck = [nodes[0]]
            discovered = []
            # run bfs
            while toCheck:
                startNode = toCheck.pop()
                for neighbor in graph.get(startNode):
                    if neighbor not in discovered:
                        discovered.append(neighbor)
                        toCheck.append(neighbor)
                        nodes.remove(neighbor)
            # add discovered graphs
            graphs.append(discovered)
        self.graphs = graphs
        return graphs

    def printGraph(self):
        for idx, graph in enumerate(BFS(self.linelist)):
            print(f"Graph {idx} is in ",color[idx]," with nodes {graph}") 

    def getGraphLines(self,linelist):

        vertices = {}
        graph_numbers = itertools.count(1)
        for v1, v2 in linelist:
            v1 = tuple(v1)
            v2 = tuple(v2)
            graph_number = vertices.get(v1) or vertices.get(v2) or next(graph_numbers)
            vertices[v1] = graph_number
            vertices[v2] = graph_number

        #print('Vertices:')
        #pprint.pprint(vertices)
        
        graphs = collections.defaultdict(list)
        for v1, v2 in linelist:
            graph_number = vertices[tuple(v1)]
            graphs[graph_number].append([v1, v2])
        return graphs

        #print('Graphs:')
        #pprint.pprint(graphs)

    def nxGraph(self,linelist):
        """
        This fines the graphs using networkx package.
        """
        linelist = self.linelist
        tmp = [tuple(tuple(j) for j in i) for i in linelist]
        graph = nx.Graph(linelist)
        i = 0
        for idx, graph in enumerate(nx.connected_components(graph)):
            print("Graph ",idx, " in ", graph,'\n\n',file=open("output.txt","a"))         
            i+=1

    def containsGraph(self,g2,g1):
        points = np.array(g1)
        vertices = np.array(g2)
        np.append(vertices,vertices[0]) # assuming this is an np array

        path = Path(vertices, closed=True)
        return np.all(path.contains_points(points))

    
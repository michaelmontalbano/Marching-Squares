#from vispy.gloo.gl import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
from MarchingSquare import *
from MS_Graph import *
import numpy as np
from netCDF4 import Dataset
import collections
import itertools
import pprint
import networkx as nx

#Globals
winHeight = 120
winWidth = 120
gridSize = 10
msHandler = -1
ESCAPE = '\033'
window = 0
showGrid = True
graphs = []


def init():    

    # Setting up values
    # name = '/localdata1/data/3Dradar/20190522/multi/MergedReflectivityQC/01.00/20190523-020310.netcdf' # use when at work
    name = r"C:\Users\User\weather\cases\20190523-020516.netcdf"
    f = Dataset(name,mode='r')
    var = f.variables['MergedReflectivityQC'][:,:] 
    #cut out all but the supercell
    storm_var = var[28:48,45:55]    
    normalizer = 1/np.amax(var)

    # Or, use this for practice
    A = np.zeros((12,12))
    #A[A<1] = -1
    for i in np.arange(1,4):
        for j in np.arange(1,4):
            A[i,j] = 1
    for i in np.arange(2,3):
        for j in np.arange(2,3):
            A[i,j] = 2

    for i in np.arange(4,9):
        for j in np.arange(4,9):
            A[i,j] = 1
    for i in np.arange(7,8):
        for j in np.arange(7,8):
            A[i,j] = 2
    print(A)
    #for i in np.arange(3,4):
    #    for j in np.arange(3,4):
    #        A[i,j] = 3

    global msHandler
    msHandler = MarchingSquareHandler(A.transpose(), (1,2,3),winWidth,winHeight,gridSize)
    #msHandler = MarchingSquareHandler(var.transpose(), (45,50,55),winWidth,winHeight,gridSize)
    msHandler.compute()      # compute linelist

    linelist= msHandler.getLineLists()[0]   # linelist is retrieved, to be used to finding the graphs
    msGraph = MS_Graph(linelist)
    

#    tmp = [tuple(tuple(j) for j in i) for i in linelist]
#    graph = nx.Graph(tmp)
    i=0
#    open('output.txt','w').close()
#    for idx, graph in enumerate(nx.connected_components(graph)):
#        print("Graph ",idx, " in ",color[i]," corresponds to vertices: ",graph,'\n\n',file=open("output.txt","a"))         
#        i+=1
      
def getGraph(linelist):
    # edge list usually reads v1 -> v2
    graph = {}
    # however these are lines so symmetry is assumed
    for l in linelist:
        v1, v2 = map(tuple, l) # what does this function do?
        graph[v1] = graph.get(v1, ()) + (v2,)      
        graph[v2] = graph.get(v2, ()) + (v1,)
    return graph

def BFS(graph):
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
    return graphs     

def getGraphLines(linelist):

    vertices = {}
    graph_numbers = itertools.count(1)
    for v1, v2 in linelist:
        v1 = tuple(v1)
        v2 = tuple(v2)
        graph_number = vertices.get(v1) or vertices.get(v2) or next(graph_numbers)
        vertices[v1] = graph_number
        vertices[v2] = graph_number
    
    graphs = collections.defaultdict(list)
    for v1, v2 in linelist:
        graph_number = vertices[tuple(v1)]
        graphs[graph_number].append([v1, v2])

def ReSizeGLScene(Width, Height):
    if Height == 0:
        Height = 1

    glViewport(0, 0, Width, Height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(0, float(Width)/float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)


def DrawGLScene():
    global lineList,showGrid
    showGrid=True
    
    glLoadIdentity()
    glOrtho(0,winWidth,winHeight,0,0.0,100.0)
    glClearColor(1,1,1,1)
    glClearDepth(1.0)
    glClear(GL_COLOR_BUFFER_BIT |GL_DEPTH_BUFFER_BIT)    
    glColor3f(0,0,0)
    glLineWidth(4)   
    gridSize = msHandler.getGridSize()
        
    if showGrid:
        glBegin(GL_LINES)
        for i in range(0,winHeight,gridSize):
            glVertex2f(i,0)
            glVertex2f(i,winHeight)
          
            glVertex2f(0,i)
            glVertex2f(winHeight,i)
        glEnd()

    lineLists = msHandler.getLineLists()
    k=0
#    print("STARTING----------------")
#    print(lineLists[0])
#    print(lineLists[1])
#    print(lineLists[2])

    all_graphs = []
    for l in lineLists:
        Graph = MS_Graph(l)
        graph = Graph.getGraph()
        #graph = getGraph(lineList)
        graphs = Graph.BFS(graph)
        j = 0
        for graph in graphs:
            all_graphs.append(graph)

    collections = []
    for idx1, g1 in enumerate(all_graphs): # you have to use the vertices
        if idx1 == len(all_graphs)-1:
            break
        for idx2, g2 in enumerate(all_graphs):
            if g1 == g2:
                pass
            if Graph.containsGraph(g1,g2) or Graph.containsGraph(g2,g1):
                collections.append((g1,g2))

    print("\n\n\n",collections)

    for idx, collection in enumerate(collections):
        for graph in collection:
            vertices = np.array(list(graph))
            glBegin(GL_LINES)
            if idx == 0 or idx == 10: # if it is 9*n, with n = 0, 1, 2, ..., n
                glColor3f(1.0,0.0,0.0)
            if idx == 1 or idx == 11: # if it is 1 + 10*n
                glColor3f(0.0,1.0,0.0)
            if idx == 2 or idx == 12:
                glColor3f(0.0,0.0,1.0)
            if idx == 3 or idx == 13:
                glColor3f(1.0,1.0,0.0)
            if idx == 4 or idx == 14:
                glColor3f(1.0,0.0,1.0)
            if idx == 5 or idx == 15:
                glColor3f(0.0,1.0,1.0)
            if idx == 6 or idx == 16:
                glColor3f(0.0,0.5,0.0)
            if idx == 7 or idx == 17:
                glColor3f(1.0,0.5,0.0) 
            if idx == 8 or idx == 18:
                glColor3f(0.5,1.0,0.0)
            if idx == 9 or idx == 19:
                glColor3f(0.5,0.0,1.0)
            for i in range(len(vertices)-1):
                if i == 0:
                    glVertex2f(graph[-1][0],graph[-1][1])
                    glVertex2f(graph[i][0],graph[i][1])
                glVertex2f(graph[i][0],graph[i][1])
                glVertex2f(graph[i+1][0],graph[i+1][1])
            glEnd()
    



    #print("I am printing collections\n",collections)
    #tmp = [tuple(tuple(j) for j in i) for i in lineList]
    #graph = nx.Graph(tmp);
    #j = 0
    #for idx, graph in enumerate(nx.connected_components(graph)):
        
        #vertices = np.array(list(graph))
        #glBegin(GL_LINES)
        #if j == 0:
            #glColor3f(1.0,0.0,0.0)
        #if j == 1:
            #glColor3f(0.0,1.0,0.0)
        #if j == 2:
            #glColor3f(0.0,0.0,1.0)
        #if j == 3:
            #glColor3f(1.0,1.0,0.0)
        #if j == 4:
            #glColor3f(1.0,0.0,1.0)
        #if j == 5:
            #glColor3f(0.0,1.0,1.0)
        #if j == 6:
            #glColor3f(0.0,0.5,0.0)
        #if j == 7:
            #glColor3f(1.0,0.5,0.0) 
        #if j == 8:
            #glColor3f(0.5,1.0,0.0)  
        #j+=1
        #for i in range(len(vertices)-1):
            #glVertex2f(vertices[i][0],vertices[i][1])
            #glVertex2f(vertices[i+1][0],vertices[i+1][1])
        #glEnd()
#
#    for i in range(len(lineList)-1):
#        dline = lineList[i]
#        glVertex2f(dline[0][0],dline[0][1])
#        glVertex2f(dline[1][0],dline[1][1])
#    glEnd()
            
    glutSwapBuffers()
            
def keyPressed(*args):
    global showGrid
    if args[0] == ESCAPE:
        sys.exit()
    elif args[0] == 's':
        if showGrid:
            showGrid=False
        else:
            showGrid=True
        

def main():
    global window
    
    glutInit(sys.argv)
    
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

    glutInitWindowSize(winWidth,winHeight)

    glutInitWindowPosition(0, 0)

    window = glutCreateWindow(b"Marching Square")
    
    glutDisplayFunc(DrawGLScene)
    glutIdleFunc(DrawGLScene)
    glutReshapeFunc(ReSizeGLScene)

    glutKeyboardFunc(keyPressed)

    init()

    glutMainLoop()

print("(s) to show/hide grid")
print("Hit ESC key to quit.")
main()

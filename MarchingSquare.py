import sys
import numpy as np

    
class MarchingSquareHandler:

    def __init__(self, values,thresholds,w,h,g):
        # copy values into a tmp
        self.container = np.ndarray(shape=(len(thresholds),w//g,h//g)) # creates an nparray to store data at different thresholds
        for count, t in enumerate(thresholds):
            tmp = values
            tmp[tmp < t] = -1
            self.container[count] = tmp
            print(values)
        self.winWidth = w
        self.winHeight = h
        self.gridSize = g
        self.thresholds = thresholds # this is a tuple but we could also use an int
        self.lineLists = np.ndarray(shape=(len(thresholds)),dtype=object)

    def printContainer(self):
        print(self.container)
        
    
    #default Values
    _nSquare = 0
    radius=0
    isovalue=0
    vertices = [] #copied from linelist
    linelist=[]
    _scVal = []

    def setWindow(self,w,h,o):
        self.winHeight = h
        self.winWidth = w
    
    def setGridSize(self,grid):
        self.gridSize = grid
        
    def setRadius(self,r):
        self.radius = r
        
    def getGridSize(self):
        return self.gridSize
    
    def getLineLists(self):
        return self.lineLists

    
    def scalarFunc(self,x,y,r): # a circle
        return (x-200)**2 + (y-200)**2 - r**2
    
    #check if scalar function intersects
    def checkifIntersects(self,_val):
        #print(_val)
        if _val[0] > 0 and _val[1] > 0 and _val[2] > 0 and _val[3] > 0:
            #print('false')
            return False
        if _val[0] < 0 and _val[1] < 0 and _val[2] < 0 and _val[3] < 0:
            #print('false')
            return False
        #print('True')
        return True

    #Get the intersected indexs
    def getIntersects(self,_val):
        #print(_val)
        index=[]
        if _val[0] * _val[1] < 0:
            index.append([0,1])
        if _val[1] * _val[2] < 0:
            index.append([1,2])
        if _val[2] * _val[3] < 0:
            index.append([2,3])
        if _val[3] * _val[0] < 0:
            index.append([3,0])
        #print(index)
        return index
        
    #Compute Scalar Values
    def compSval(self,c):
        lenY = len(np.arange(0,self.winHeight,self.gridSize))
        lenX = len(np.arange(0,self.winWidth,self.gridSize))
        for y in range(lenY):
            for x in range(lenX):
                self._scVal[x][y] = self.container[c][x][y]
                #self._scVal[x][y] = self.scalarFunc(self.gridSize*x,self.gridSize*y,self.radius)
        
    #Find the intersection Point
    def intersectionPoint(self,p1,p2,isoValue,v1,v2):
        _p=[0,0]
        _p[0] = p1[0] + (isoValue - v1)*(p2[0] - p1[0] ) / (v2-v1)
        _p[1] = p1[1] + (isoValue - v1)*(p2[1] - p1[1] ) / (v2-v1)
        # round numbers to 6 digits - mmontalbano
        _p[0] = round(_p[0],6)
        _p[1] = round(_p[1],6)
        return _p
        
    #Get all the Data about square
    def getSquareData(self,n): #returns sqaures sv and vertices
        c=int(n//((self.winHeight//self.gridSize)-1)) # mmontalbano
        r=int(n%((self.winHeight//self.gridSize)-1))  # mmontalbano
        #print(r,c)
        sv=[self._scVal[c][r],self._scVal[c][r+1],self._scVal[c+1][r+1],self._scVal[c+1][r]]  # 
        vertices =[[self.gridSize*c,self.gridSize*r],[self.gridSize*c,self.gridSize*(r+1)],[self.gridSize*(c+1),self.gridSize*(r+1)],[self.gridSize*(c+1),self.gridSize*r]] 
        return [sv,vertices]
        
    #Check if Zero
    def checkSingularity(self,sv):
        found=False
        index=[]
        for i in np.arange(0,len(sv)):
            if sv[i] == 0:
                found = True
                index.append(i)
        return [found,index]
    
    #Computes the line list
    def compute(self):
        for count in range(len(self.thresholds)):
            j=0
            k=0
            p3=0
            p4=0
            self._scVal = np.zeros(((self.winWidth//self.gridSize),(self.winHeight//self.gridSize)))
            _nSquare = ((self.winHeight/self.gridSize)-1)*((self.winWidth/self.gridSize)-1)
            self.compSval(count)
            for i in np.arange(0,_nSquare):
                [_sv,_vert] = self.getSquareData(i)
                if self.checkifIntersects(_sv):
                    isSig=self.checkSingularity(_sv)
                    if isSig[0]:
                        if len(isSig[1]) > 1: #two point Singularity
                            p1 = _vert[isSig[1][0]]
                            p2 = _vert[isSig[1][1]]
                        else: #one point Singularity
                            #check if other intersection exists
                            intPoint = self.getIntersects(_sv)
                            if len(intPoint) == 0:
                                p1 = _vert[isSig[1][0]]
                                p2 = _vert[isSig[1][0]]
                            else:
                                [_i1] = self.getIntersects(_sv)
                                p1 =self.intersectionPoint(_vert[_i1[0]],_vert[_i1[1]],self.isovalue,_sv[_i1[0]],_sv[_i1[1]])
                                p2 = _vert[isSig[1][0]]
                                
                    else:
                        if len(self.getIntersects(_sv)) > 2:
                            [i1,i2,i3,i4] = self.getIntersects(_sv)    							# determines whether and where to put intersecting lines
                            [_i1,_i2] = [i1,i2]                        							# retrieves the lines along which the vertices will be placed 
                            p1=self.intersectionPoint(_vert[_i1[0]],_vert[_i1[1]],self.isovalue,_sv[_i1[0]],_sv[_i1[1]])	# retrieves the first vertex, using linear interpolation
                            p2=self.intersectionPoint(_vert[_i2[0]],_vert[_i2[1]],self.isovalue,_sv[_i2[0]],_sv[_i2[1]])
                            [_i3,_i4] = [i3,i4]      
                            p3=self.intersectionPoint(_vert[_i3[0]],_vert[_i3[1]],self.isovalue,_sv[_i3[0]],_sv[_i3[1]])
                            p4=self.intersectionPoint(_vert[_i4[0]],_vert[_i4[1]],self.isovalue,_sv[_i4[0]],_sv[_i4[1]])                        
                        else:
                            [_i1,_i2]=self.getIntersects(_sv) 
                            p1=self.intersectionPoint(_vert[_i1[0]],_vert[_i1[1]],self.isovalue,_sv[_i1[0]],_sv[_i1[1]])
                            p2=self.intersectionPoint(_vert[_i2[0]],_vert[_i2[1]],self.isovalue,_sv[_i2[0]],_sv[_i2[1]])
                    # if len(self.linelist) > 2:
                    #     if (np.asarray(p1) not in np.asarray(self.linelist)) and (np.asarray(p2) not in np.asarray(self.linelist)) or (np.asarray(p3) not in np.asarray(self.linelist) and np.asarray(p4) not in np.asarray(self.linelist) and p3 != 0 and p4 !=0):
                    #         self.graphs[j] = np.asarray(self.linelist)[k:] #fills the graph element with the set
                    #         k = len(np.asarray(self.linelist))
                    #         j = j+1
                    self.linelist.append([p1,p2])
                    if p3 != 0 and p4 != 0:
                        self.linelist.append([p3,p4])
                        p3 = 0
                        p4 = 0
            self.lineLists[count] = self.linelist.copy()
            self.linelist = []
            #    if i == _nSquare-1:
            #        self.graphs[j] = np.asarray(self.linelist)[k:]
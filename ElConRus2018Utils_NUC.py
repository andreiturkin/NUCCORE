############################################################################################
#                              The Non-uniform Covering Approach
############################################################################################
# Abstract Methods
import abc
# numpy and math
import numpy as np
from math import sqrt
# Tree
from ete3 import Tree
# Saving
import cPickle
import os
from interval import interval
# Plotting
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from ElConRus2018Utils_Plotting import PlottingTree

class Box(object):
    def __init__(self, cpoint, sides):
        self.__cpoint = np.array(cpoint)
        self.__sides = np.array(sides)
        self.__diam = sqrt(sum(side*side for side in sides))
        self.__bnds = np.array([(cpoint[idx], cpoint[idx]+side) for idx, side in enumerate(sides)])

    def getDim(self):
        return self.__cpoint.shape[0]

    def getDiam(self):
        return self.__diam

    def getSides(self):
        return np.copy(self.__sides)

    def getCorner(self):
        return np.copy(self.__cpoint)

    def Split(self):
        # Find an index of the longest side
        idx = max(enumerate(self.__sides), key=lambda x: x[1])[0]
        # Bisect by the longest side
        # To get the first box
        lBox_cpoint = np.copy(self.__cpoint)
        lBox_sides = np.copy(self.__sides)
        lBox_sides[idx] = lBox_sides[idx]/2.0
        lBox = Box(lBox_cpoint, lBox_sides)
        # To get the second one
        rBox_cpoint = np.copy(self.__cpoint)
        rBox_sides = np.copy(self.__sides)
        rBox_cpoint[idx] = rBox_cpoint[idx] + rBox_sides[idx]/2.0
        rBox_sides[idx] = rBox_sides[idx]/2.0
        rBox = Box(rBox_cpoint, rBox_sides)
        # Return the obtained boxes
        return lBox, rBox

    def getBounds(self):
        return np.copy(self.__bnds)

    def getInterval(self):
        bnds = np.copy(self.__bnds)
        xmin = bnds[0][0]
        xmax = bnds[0][1]
        ymin = bnds[1][0]
        ymax = bnds[1][1]
        return (interval[xmin, xmax], interval[ymin, ymax])

    def __str__(self):
        return '<Box: {}, {}>'.format(self.__cpoint, self.__sides)

class CoveringTree(object):
############################################################################################
# Constructor
############################################################################################
    __metaclass__ = abc.ABCMeta
    def __init__(self, iBox, idelta=0.0, ShowCovPrc=False, ieps=0.0):
        # Initialize initial Space where the workspace lie
        self.__Xspace = iBox
        # Initialize the minimal size of the rectangle
        self.__delta = idelta
        # Initialize the epsilon value
        self.__eps = ieps
        # Show the covering process
        self.__bShow = ShowCovPrc
        # Number of processed levels of the tree and the number of iterations
        self.__nLevelsProcessed = None
        self.__nIterations = None

    @abc.abstractmethod
    def getMinMaxVal(self, bounds, diam):
        raise NotImplementedError

############################################################################################
# Public Members
############################################################################################
    def getCoverigAccuracy(self):
        return self.__delta
    def getResProcessedLevels(self):
        return self.__nLevelsProcessed
    def getResIterations(self):
        return self.__nIterations

    def getSolution(self, maxLevels):

        # Initialize the Root of the Tree and additional variables
        self.__initTree(self.__Xspace)
        # Uncomment if it necessary to get information on the initial box
        # print 'The diameter of the initial box is {}'.format(self.__Xspace.getDiam())
        bExit = False
        nIter = 0

        for curLevel in range(0, maxLevels):
            # Get all the rectangles that are on some level of the tree
            curLevelNodes = self.__sTree.get_leaves_by_name(name='{}'.format(curLevel))
            # Uncomment if you would like to see the progress of calculation for every level
            # print 'The {}th layer of boxes with the diameter equals {} is precessed'.format(curLevel, \
            #         curLevelNodes[0].Box.getDiam())
            # Loop over the rectangles
            for curLevelNode in curLevelNodes:
                nIter = nIter + 1
                #Get a box from the tree level
                oBox = curLevelNode.Box
                #Analyze it
                cont, inrange = self.__analyseBox(oBox)
                #Classify it
                inQE, inQI, bExit = self.__placeBox(oBox, cont, inrange)
                #Save the obtained results
                if cont and (curLevel < maxLevels-1) and not bExit:
                    # (oRleft, oRright) = self.__getNewRect(oRect, curLevel)
                    (oRleft, oRright) = oBox.Split()
                    self.__addToTree(curLevelNode, oRleft, oRright, curLevel + 1)
                else:
                    #save results to the analyzed node
                    curLevelNode.add_feature('Inrange', inrange)
                    curLevelNode.add_feature('inQI', inQI)
                    curLevelNode.add_feature('inQE', inQE)
                #Draw the coveing process
                if self.__bShow:
                    # Call a method from CableCon2017_Plotting.py,
                    # which must be in self after calling PlottingTree.__init__(...)
                    if 'drawBox' in dir(self):
                        self.drawBox(oBox, inrange, inQI, inQE)
            #All of the rectangles could be obtained on the next iterations are too small
            #so break it
            if bExit:
                # Uncomment if you would like to get information on the processed levels
                # and iterations
                # print 'Number of levels were processed: {}'.format(curLevel)
                # print 'Number of iterations: {}'.format(nIter)
                self.__nLevelsProcessed = curLevel
                self.__nIterations = nIter
                if self.__bShow:
                    plt.show()
                break

    def getTree(self):
        T = {'iBox': self.__Xspace, 'iDelta': self.__delta,
             'iEps': self.__eps, 'bShow': self.__bShow, 'Tree': self.__sTree}
        return T

    def SaveSolution(self, fName):
        T = self.getTree()
        cPickle.dump(T, open(fName, 'wb'))

    def isFileExist(self, fName):
        return os.path.isfile(fName)

    def LoadSolution(self, fName):
        T = cPickle.load(open(fName, 'rb'))
        self.__setTree(T)

############################################################################################
# Private Members
############################################################################################
    def __analyseBox(self, iBox):

        inrange = False
        cont = True

        # if iBox.getCorner()[0] == -0.125 and iBox.getCorner()[1] == -14.0 and iBox.getSides()[1] == 0.5:
        #     print iBox

        # Call an abstract method
        minval, maxval = self.getMinMaxVal(iBox)
        #The whole rectangle is a part of the solution -> save it
        if maxval < -self.__eps:
            #mark it as in range
            inrange = True
            cont = False
            return cont, inrange

        #There is no solution for the rectangle -> get rid of it
        if minval > self.__eps:
            #mark it as out of range
            inrange = False
            cont = False
            return cont, inrange

        #The rectangle should be processed further
        return cont, inrange

    def __placeBox(self, iBox, cont, inrange):
        inQE = False
        inQI = False
        bExit = False
        #The diameter of the rectangle is less than or equal to the predefined delta value
        if iBox.getDiam() <= self.__delta:
            #It is too small but we have to analyze it before quit
            if cont:
                inQI = False
                inQE = True
            else:
                if inrange:
                    inQI = True
                    inQE = False
                #else: defaults
            #Return the result on the next iteration
            bExit = True
        #Otherwise
        else:
            if inrange:
                inQI = True
                inQE = False
            #else: defaults
        return inQE, inQI, bExit

    @staticmethod
    def __addToTree(motherNode, iBox1, iBox2, childNodeLevel):
        # and add the nodes as children.
        oNode2 = motherNode.add_child(name='{}'.format(childNodeLevel))
        oNode1 = motherNode.add_child(name='{}'.format(childNodeLevel))
        #add features
        oNode2.add_feature('Box', iBox2)
        oNode1.add_feature('Box', iBox1)

    def __initTree(self, Xspace):
        self.__sTree = Tree('0;')
        # name here is the level of the tree
        motherNode = self.__sTree.search_nodes(name='0')[0]
        motherNode.add_feature('Box', Xspace)

    def __setTree(self, T):
        # Initialize initial Space where the workspace lie
        self.__Xspace = T['iBox']
        # Initialize the minimal size of the rectangle
        self.__delta = T['iDelta']
        # Initialize the epsilon value
        self.__eps = T['iEps']
        # Show the covering process
        self.__bShow = T['bShow']
        # The Tree sturcture
        self.__sTree = T['Tree']



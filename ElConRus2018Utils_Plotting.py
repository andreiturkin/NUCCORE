# Abstract Methods
import abc
from math import pi
# Numpy
import numpy as np
# Date and Time
import datetime
# Plotting 2D boxes
import matplotlib.pyplot as plt
import matplotlib.patches as patches
# Plotting 3D boxes
from mpl_toolkits.mplot3d import Axes3D
# Tree Structure
from ete3 import Tree
from interval import interval
# Saving as a json file
from ElConRus2018Utils_jsonSaving import saveDataToFile

# Refinement
from scipy import optimize

class PlottingTree(object):
############################################################################################
# Constructor
############################################################################################
    __metaclass__ = abc.ABCMeta
    def __init__(self, iBox, ShowCovPrc):
        if ShowCovPrc:
            self.InitPlottingFacilities(iBox=iBox, Prj2D=True, idxs=[2,], vals=[(10.0/180.0)*pi,])

########################################################################################
# Plotting
########################################################################################
    @abc.abstractmethod
    def AdditionalPlotting(self, ax):
        raise NotImplementedError

    def InitPlottingFacilities(self, iBox, Prj2D=True, idxs=[2,], vals=[(10.0/180.0)*pi,]):
        #Initialize plotting facilities
        self.__fig = plt.figure()
        if iBox.getSides().shape[0] == 2 or Prj2D:
            self.__ax = self.__fig.add_subplot(111)
            self.__ax.axis('scaled')
            bnds = iBox.getBounds()
            self.__ax.axis([bnds[0][0], bnds[0][1], bnds[1][0], bnds[1][1]])
            self.indxs = idxs
            self.vals = vals
        else:
            self.__ax = self.__fig.add_subplot(111, projection='3d')
            self.__ax.axis('scaled')
            bnds = iBox.getBounds()
            self.__ax.set_xlim(bnds[0][0], bnds[0][1])
            self.__ax.set_ylim(bnds[1][0], bnds[1][1])
            self.__ax.set_zlim(bnds[2][0], bnds[2][1])
            self.__ax._axis3don = False

    def drawCircle(self, center, radius):
        self.__ax.add_patch(patches.Circle(center, radius, fill=False, lw=1, ls='dashed', color='black'))

    def drawArc(self, center, radius, psi):
        self.__ax.add_patch(patches.Arc(center, 2*radius, 2*radius, 0.0, psi[0]*180.0/np.pi, psi[1]*180.0/np.pi, color='orange'))

    def drawLine(self, center, radius, psi):
        for angle in psi:
            x1 = center[0] + radius[0] * np.cos(angle)
            y1 = center[1] + radius[0] * np.sin(angle)

            x2 = center[0] + radius[1] * np.cos(angle)
            y2 = center[1] + radius[1] * np.sin(angle)

            self.__ax.plot([x1, x2], [y1, y2], color='orange')

    def __getBoxFeatures(self, inQI, inQE):
        #Internal
        if inQI and (not inQE):
            edgeColor = 'black'
            LineStyle = 'solid'
            LineWidth = 0.3
            Alpha = 0.3
        #External
        if inQE and (not inQI):
            edgeColor = 'red'
            LineStyle = 'solid'
            LineWidth = 0.3
            Alpha = 0.3
        #Out of range
        if (not inQE) and (not inQI):
            edgeColor = 'green'
            LineStyle = 'solid'
            LineWidth = 0.3
            Alpha = None
        return edgeColor, LineStyle, LineWidth, Alpha, inQI

    def __drawBox(self, iBox, edgeColor, lineStyle, lineWidth, Alpha, Fill):
        sides = iBox.getSides()[:2]
        self.__ax.add_patch(patches.Rectangle(iBox.getCorner()[:2],       # (x,y)
                                              sides[0],                   # width
                                              sides[1],                   # height
                                              fill=Fill,
                                              alpha=Alpha,
                                              linestyle=lineStyle,
                                              edgecolor=edgeColor,
                                              lw=lineWidth))

    def __drawBox2D(self, iBox, fillIt, inQI=False, inQE=True):
        edgeColor, lineStyle, lineWidth, Alpha, Fill = self.__getBoxFeatures(inQI, inQE)
        self.__drawBox(iBox, edgeColor, lineStyle, lineWidth, Alpha, Fill)

    def __drawProjection2D(self, iBox, fillIt, inQI=False, inQE=True):
        a = interval[iBox.getCorner()[self.indxs[0]], iBox.getCorner()[self.indxs[0]] + iBox.getSides()[self.indxs[0]]]
        if self.vals[0] in a:
            edgeColor, lineStyle, lineWidth, Alpha, Fill = self.__getBoxFeatures(inQI, inQE)
            self.__drawBox(iBox, edgeColor, lineStyle, lineWidth, Alpha, Fill)
    def __drawBox3D(self, iBox, fillIt, inQI=False, inQE=True):
        edgeColor, LineStyle, LineWidth, Alpha = self.__getBoxFeatures(inQI, inQE)

        sides = iBox.getSides()
        corner = iBox.getCorner()
        I = np.eye(sides.shape[0])*sides
        for idx, e in enumerate(I):
            self.__ax.plot3D(*zip(corner, corner + e), color=edgeColor, linewidth=LineWidth)
            self.__ax.plot3D(*zip(corner + e, corner + e + I[:, idx-1]), color=edgeColor, linewidth=LineWidth)
            self.__ax.plot3D(*zip(corner + e, corner + e + I[:, idx-2]), color=edgeColor, linewidth=LineWidth)
            self.__ax.plot3D(*zip(corner+sides, corner + sides - e), color=edgeColor, linewidth=LineWidth)

    def drawBox(self, iBox, fillIt, inQI=False, inQE=True):
        if iBox.getDim() == 2:
            self.__drawBox2D(iBox, fillIt, inQI, inQE)
        if iBox.getDim() == 3:
            self.__drawProjection2D(iBox, fillIt, inQI, inQE)
        if iBox.getDim() > 3:
            print 'TODO: Project it onto a three-dimensional hyperplane'

    def saveResultAsImage(self, iTree, fileName='./Images/{0}__{1:02d}_{2:02d}_{3:02d}_covering.eps'.format(datetime.date.today(), \
                                            datetime.datetime.now().hour,\
                                            datetime.datetime.now().minute,\
                                            datetime.datetime.now().second),\
                                            AddRings=False):
        print 'Saving the image...'
        if not hasattr(self, '__fig'):
            self.InitPlottingFacilities(iTree.search_nodes(name='0')[0].Box)
        else:
            #Get information on the initial box
            bnds = iTree.search_nodes(name='0')[0].Box.getBounds()
            self.__ax.axis([bnds[0][0], bnds[0][1], bnds[1][0], bnds[1][1]])

        print 'Drawing rectangles...'
        for leaf in iTree.iter_leaves():
            #Draw the rectangle with edges
            self.drawBox(leaf.Box, leaf.Inrange, leaf.inQI, leaf.inQE)

        if AddRings:
            print 'Additional Plotting...'
            # Call an abstract method
            self.AdditionalPlotting(self.__ax)
        print 'Drawing the Figure...'
        plt.draw()
        plt.pause(1)
        #Save the result
        print 'Saving the image...'
        self.__fig.savefig(fileName, dpi=1200)
        print 'The image has been saved correctly'

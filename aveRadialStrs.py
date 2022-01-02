# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2019 replay file
# Internal Version: 2018_09_25-02.41.51 157541
# Run by wgm on Mon Dec  9 14:52:23 2019
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import numpy
executeOnCaeStartup()

openMdb('twd_cut100_radstrsDissertation.cae')
session.viewports['Viewport: 1'].view.setProjection(projection=PARALLEL)
p = mdb.models['Model-1'].parts['Part-1']
mdb.models['Model-1'].parts['Part-1'].setValues(geometryRefinement=EXTRA_FINE)

minR=100000
maxR=0
for vi in p.vertices:
	pCoordR=vi.pointOn[0][0]
	if pCoordR<minR:
		minR=pCoordR
	if pCoordR>maxR:
		maxR=pCoordR

datumPlaneNum=50
dR=(maxR-minR)/(datumPlaneNum+1)
datumPlaneSet=[]
datumPlaneRCoord=[]
for iter in range(0,datumPlaneNum):
	datumPlaneRCoord.append(minR+(iter+1)*dR)
	datumPlaneSet.append(p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=minR+(iter+1)*dR))

f = p.faces
d = p.datums
for datumPlane in datumPlaneSet:
	p.PartitionFaceByDatumPlane(datumPlane=d[datumPlane.id], faces=f.findAt((maxR,0,0)))

datumVerticesCoord=[]
for iter in range(0,datumPlaneNum):
	vertRPlane=p.vertices.getByBoundingBox(xMin=datumPlaneRCoord[iter]-0.01*dR,yMin=-100000,zMin=-1,xMax=datumPlaneRCoord[iter]+0.01*dR,yMax=100000,zMax=1)
	datumVerticesCoord.append((vertRPlane[0].pointOn[0],vertRPlane[1].pointOn[0]))

vertRPlane=p.vertices.getByBoundingBox(xMin=minR-0.01*dR,yMin=-100000,zMin=-1,xMax=minR+0.01*dR,yMax=100000,zMax=1)
datumVerticesCoord.insert(0,(vertRPlane[0].pointOn[0],vertRPlane[1].pointOn[0]))
vertRPlane=p.vertices.getByBoundingBox(xMin=maxR-0.01*dR,yMin=-100000,zMin=-1,xMax=maxR+0.01*dR,yMax=100000,zMax=1)
datumVerticesCoord.append((vertRPlane[0].pointOn[0],vertRPlane[1].pointOn[0]))

import visualization
import numpy as np
o1 = session.openOdb(name='F:/wgm/lunpan/twdlunpanGA/diskCut100.odb')
session.viewports['Viewport: 1'].setValues(displayedObject=o1)
session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
    variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(COMPONENT, 
    'S11'), )

aveRadStrsList=[]
for iter in range(0,datumPlaneNum+2):
	session.Path(name='Path-1', type=POINT_LIST, expression=datumVerticesCoord[iter])
	
	pth = session.paths['Path-1']
	session.XYDataFromPath(name='XYData-1', path=pth, includeIntersections=False, 
		projectOntoMesh=False, pathStyle=UNIFORM_SPACING, numIntervals=500, 
		projectionTolerance=0, shape=UNDEFORMED, labelType=TRUE_DISTANCE, 
		removeDuplicateXYPairs=True, includeAllElements=False)
	
	pathDat=session.xyDataObjects['XYData-1']
	xCoord=[]
	yCoord=[]
	for pathDatEntry in pathDat:
		xCoord.append(pathDatEntry[0])
		yCoord.append(pathDatEntry[1])
	
	aveRadStrsList.append(np.trapz(yCoord,xCoord)/(max(xCoord)))
	
	del session.paths['Path-1']
	del session.xyDataObjects['XYData-1']

maxAveRadStrs=max(aveRadStrsList)
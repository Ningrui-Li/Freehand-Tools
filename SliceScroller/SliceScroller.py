import os
from inspect import getsourcefile
from os.path import abspath 
import unittest
import numpy as np
import subprocess
import module_locator
from __main__ import vtk, qt, ctk, slicer


class SliceScroller:
  def __init__(self, parent):
    parent.title = "Freehand Slice Scroller" 
    parent.categories = ["Freehand"]
    parent.dependencies = []
    parent.contributors = ["Ningrui Li"] 
    parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    parent.acknowledgementText = "zzzzzzzzzzzzzzzz" # replace with organization, grant and thanks.
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.

class SliceScrollerWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()
    self.scene = slicer.mrmlScene
    self.scene.SaveStateForUndo()
  def setup(self):
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "SliceScroller Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    # reload and test button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadAndTestButton = qt.QPushButton("Reload and Test")
    self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
    reloadFormLayout.addWidget(self.reloadAndTestButton)
    self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)
    
    # Slice Scrolling Area
    scrollingCollapsibleButton = ctk.ctkCollapsibleButton()
    scrollingCollapsibleButton.text = "Slice Scrolling"
    self.layout.addWidget(scrollingCollapsibleButton)
    # Layout within the scrolling collapsible button
    scrollingFormLayout = qt.QFormLayout(scrollingCollapsibleButton)

    # directory selection layout
    self.directorySelectionButton = ctk.ctkDirectoryButton()
    self.directorySelectionButton.text = "C:/Users/Rui/Dropbox/Documents/Documents/Duke/Nightingale Lab/magnetic_tracking/Freehand-Tools/SliceScroller/data/"
    self.directorySelectionButton.directory = self.directorySelectionButton.text
    scrollingFormLayout.addRow("Directory", self.directorySelectionButton)

    # Slice selection scroller
    self.sliceSlider = ctk.ctkSliderWidget()
    self.sliceSlider.decimals = 0
    self.sliceSlider.enabled = True
    scrollingFormLayout.addRow("Slices", self.sliceSlider)

    # orientation layout + sliders
    orientationCollapsibleButton = ctk.ctkCollapsibleButton()
    orientationCollapsibleButton.text = "Orientation"
    self.layout.addWidget(orientationCollapsibleButton)
    
    orientationFormLayout = qt.QFormLayout(orientationCollapsibleButton)
    
    # Tracking system input button
    self.trackingSysButton = qt.QPushButton("Read Position")
    orientationFormLayout.addWidget(self.trackingSysButton)

    # radius scaling slider
    scalingCollapsibleButton = ctk.ctkCollapsibleButton()
    scalingCollapsibleButton.text = "Sphere Radius Scaling"
    self.layout.addWidget(scalingCollapsibleButton)
    scalingFormLayout = qt.QFormLayout(scalingCollapsibleButton)

    # x, y, z plane center position sliders
    self.xSlider = ctk.ctkSliderWidget()
    self.xSlider.decimals = 2
    self.xSlider.enabled = True
    self.xSlider.maximum = 1
    self.xSlider.minimum = -1
    self.xSlider.value = 0
    self.xSlider.singleStep = 0.01
    orientationFormLayout.addRow("Center - X Position", self.xSlider)

    self.ySlider = ctk.ctkSliderWidget()
    self.ySlider.decimals = 2
    self.ySlider.enabled = True
    self.ySlider.maximum = 1
    self.ySlider.minimum = -1
    self.ySlider.value = 0   
    self.ySlider.singleStep = 0.01
    orientationFormLayout.addRow("Center - Y Position", self.ySlider)

    self.zSlider = ctk.ctkSliderWidget()
    self.zSlider.decimals = 2
    self.zSlider.enabled = True
    self.zSlider.maximum = 1
    self.zSlider.minimum = -1
    self.zSlider.value = 0
    self.zSlider.singleStep = 0.01
    orientationFormLayout.addRow("Center - Z Position", self.zSlider)

    # sphere size radius slider
    self.scalingSlider = ctk.ctkSliderWidget()
    self.scalingSlider.decimals = 0
    self.scalingSlider.enabled = True
    self.scalingSlider.maximum = 0.5
    self.scalingSlider.minimum = 0
    self.scalingSlider.singleStep = 0.01
    self.scalingSlider.value = 0.05
    scalingFormLayout.addRow("Radius", self.scalingSlider)

    # make connections between valueChanged/coordinatesChanged signals and
    # methods that connect back to the logic.
    self.directorySelectionButton.connect('directoryChanged(QString)', self.onDirectoryChanged)
    self.sliceSlider.connect('valueChanged(double)', self.onSliderValueChanged)
    self.trackingSysButton.connect('clicked()', self.onTrackingSystem)
    self.xSlider.connect('valueChanged(double)', self.onXPositionValueChanged)    
    self.ySlider.connect('valueChanged(double)', self.onYPositionValueChanged)    
    self.zSlider.connect('valueChanged(double)', self.onZPositionValueChanged)    
   
    self.scalingSlider.connect('valueChanged(double)', self.onScalingValueChanged)
    
    # declare logic variable that updates image plane properties based on values passed
    # to it from the user interface
    self.logic = SliceScrollerLogic()

    # add vertical spacing
    self.layout.addStretch(1)

  # The following methods are called when a slider/coordinate value changes.
  # Slider values and coordinates and passed down, and occasionally, results are
  # returned so as to update the slider values.

  # For example, when P, Q, or R coordinates change, the center of the plane changes such that
  # it becomes the point on the plane closest to the origin.

  def onDirectoryChanged(self, value):
    self.directorySelectionButton.text = self.directorySelectionButton.directory
    p = subprocess.Popen(["ls", self.directorySelectionButton.directory + "/"], stdout = subprocess.PIPE)
    fileList, error = p.communicate()
    fileList = fileList.split("\n")
    imageList = []
    
    for file in fileList:
        if file.endswith('.png'):
            imageList.append(file)
    
    self.sliceSlider.maximum = len(imageList)
    self.sliceSlider.value = 0 
    
    self.logic.loadImages(self.directorySelectionButton.directory + "/", imageList)
    
  def onSliderValueChanged(self, value):
    # call to selectSlice updates the scene with the selected slice.
    # returns a Slice object called currentSlice. This is used to
    # update the slider values to correctly reflect what is
    # currently shown in the scene.
    currentSlice = self.logic.selectSlice(int(value))

    # Updating slider values and coordinates
    self.xSlider.value = currentSlice.x
    self.ySlider.value = currentSlice.y
    self.zSlider.value = currentSlice.z
    
    self.pointPCoordinateBox.coordinates = ','.join(str(coord) for coord in currentSlice.PCoordinates)
    self.pointQCoordinateBox.coordinates = ','.join(str(coord) for coord in currentSlice.QCoordinates)
    self.pointRCoordinateBox.coordinates = ','.join(str(coord) for coord in currentSlice.RCoordinates)
    
    self.rotationSlider.value = currentSlice.planeRotation
    self.xAxisSlider.value = currentSlice.xAxisValue
    self.yAxisSlider.value = currentSlice.yAxisValue
    self.scalingSlider.value = currentSlice.radius
    
  def onTrackingSystem(self):
    posTrackDirectory = abspath(getsourcefile(lambda _: None))
    posTrackDirectory = posTrackDirectory.replace("SliceScroller.py", "")
    os.chdir(posTrackDirectory)
    os.system("PDIconsole.exe")
    positionFile = open(posTrackDirectory + 'test.txt', 'r')

    positionFile.readline()
    nextLine = positionFile.readline()
    measurementCounter = 0
    origin = [0, 0, 0]
    while not (nextLine.startswith("Reading")):
        reading = [float(x) for x in nextLine.split()]
        origin = np.add(origin, reading[0:3])
        nextLine = positionFile.readline()
        measurementCounter += 1
    origin = np.divide(origin, measurementCounter)

    nextLine = positionFile.readline()
    measurementCounter = 0
    Pcoords = [0, 0, 0]
    while not (nextLine.startswith("Reading")):
        reading = [float(x) for x in nextLine.split()]
        Pcoords = np.add(Pcoords, reading[0:3])
        nextLine = positionFile.readline()
        measurementCounter += 1
    Pcoords = np.divide(Pcoords, measurementCounter)

    nextLine = positionFile.readline()
    measurementCounter = 0
    Qcoords = [0, 0, 0]
    while not (nextLine.startswith("Reading")):
        reading = [float(x) for x in nextLine.split()]
        Qcoords = np.add(Qcoords, reading[0:3])
        nextLine = positionFile.readline()
        measurementCounter += 1
    Qcoords = np.divide(Qcoords, measurementCounter)

    nextLine = positionFile.readline()
    measurementCounter = 0
    Rcoords = [0, 0, 0]
    while (nextLine):
        reading = [float(x) for x in nextLine.split()]
        Rcoords = np.add(Rcoords, reading[0:3])
        nextLine = positionFile.readline()
        measurementCounter += 1
    Rcoords = np.divide(Rcoords, measurementCounter)

    positionFile.close()
    
    Pcoords = np.subtract(Pcoords, origin)
    Qcoords = np.subtract(Qcoords, origin)
    Rcoords = np.subtract(Rcoords, origin)
    
    self.pointPCoordinateBox.coordinates = ','.join(str(coord) for coord in Pcoords)
    self.pointQCoordinateBox.coordinates = ','.join(str(coord) for coord in Qcoords)
    self.pointRCoordinateBox.coordinates = ','.join(str(coord) for coord in Rcoords)
    
    self.logic.setPCoords(Pcoords)
    self.logic.setQCoords(Qcoords)
    newCenter = self.logic.setRCoords(Rcoords)
    
    self.xSlider.value = newCenter[0]
    self.ySlider.value = newCenter[1]
    self.zSlider.value = newCenter[2]
    
  def onXPositionValueChanged(self, value):
    self.logic.setXPosition(value)

  def onYPositionValueChanged(self, value):
    self.logic.setYPosition(value)

  def onZPositionValueChanged(self, value):
    self.logic.setZPosition(value)

  # For these methods, the actual value doesn't actually matter.
  # It only matters that this function is called when there is a change in coordinates, so 
  # coordinates can be updated once a change is detected.
  def onPCoordinatesChanged(self, value):
    coords = [float(x) for x in self.pointPCoordinateBox.coordinates.split(',')]
    newCenter = self.logic.setPCoords(coords)
    self.xSlider.value = newCenter[0]
    self.ySlider.value = newCenter[1]
    self.zSlider.value = newCenter[2]

  def onQCoordinatesChanged(self, value):
    coords = [float(x) for x in self.pointQCoordinateBox.coordinates.split(',')]
    newCenter = self.logic.setQCoords(coords)
    self.xSlider.value = newCenter[0]
    self.ySlider.value = newCenter[1]
    self.zSlider.value = newCenter[2]

  def onRCoordinatesChanged(self, value):
    coords = [float(x) for x in self.pointRCoordinateBox.coordinates.split(',')]
    newCenter = self.logic.setRCoords(coords)
    self.xSlider.value = newCenter[0]
    self.ySlider.value = newCenter[1]
    self.zSlider.value = newCenter[2]

  def onRotationValueChanged(self, value):
    self.logic.setRotationValue(value)

  def onXAxisValueChanged(self, value):
    self.logic.setXAxisValue(value)

  def onYAxisValueChanged(self, value):
    self.logic.setYAxisValue(value)

  def onScalingValueChanged(self, value):
    self.logic.setScaling(value)

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    logic = SliceScrollerLogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    screenshotScaleFactor = int(self.screenshotScaleFactorSliderWidget.value)
    print("Run the algorithm")
    logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), enableScreenshotsFlag,screenshotScaleFactor)

  def onReload(self,moduleName="SliceScroller"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    import imp, sys, os, slicer
    self.scene.Undo()
    widgetName = moduleName + "Widget"

    # reload the source code
    # - set source file path
    # - load the module to the global space
    filePath = eval('slicer.modules.%s.path' % moduleName.lower())
    p = os.path.dirname(filePath)
    if not sys.path.__contains__(p):
      sys.path.insert(0,p)
    fp = open(filePath, "r")
    globals()[moduleName] = imp.load_module(
        moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
    fp.close()

    # rebuild the widget
    # - find and hide the existing widget
    # - create a new widget in the existing parent
    parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent().parent()
    for child in parent.children():
      try:
        child.hide()
      except AttributeError:
        pass
    # Remove spacer items
    item = parent.layout().itemAt(0)
    while item:
      parent.layout().removeItem(item)
      item = parent.layout().itemAt(0)

    # delete the old widget instance
    if hasattr(globals()['slicer'].modules, widgetName):
      getattr(globals()['slicer'].modules, widgetName).cleanup()

    # create new widget inside existing parent
    globals()[widgetName.lower()] = eval(
        'globals()["%s"].%s(parent)' % (moduleName, widgetName))
    globals()[widgetName.lower()].setup()
    setattr(globals()['slicer'].modules, widgetName, globals()[widgetName.lower()])
    
  def onReloadAndTest(self,moduleName="SliceScroller"):
    try:
      self.onReload()
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest()
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(), 
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")

class SliceScrollerLogic:
  """This class should implement all the actual 
  computation done by your module.  The interface 
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    #Creating list of all image slices
    imgFilePrefix =  'C:\\Users\\Rui\\Dropbox\\Documents\\Documents\\Duke\\Nightingale Lab\\magnetic_tracking\\Freehand-Tools\\SliceScroller\\data\\'
    p = subprocess.Popen(["ls", imgFilePrefix], stdout = subprocess.PIPE)
    fileList, error = p.communicate()
    fileList = fileList.split("\n")
    
    imageList = []
    
    for file in fileList:
        if file.endswith('.png'):
            imageList.append(file)
      
    self.sliceList = []
    for name in imageList:
      self.sliceList.append(Slice(imgFilePrefix + name))

    self.scene = slicer.mrmlScene
    self.scene.SetUndoOn()
    self.scene.SaveStateForUndo(self.scene.GetNodes())

    self.currentSlice = self.sliceList[0]

    # yay, adding images to slicer
    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetCenter(self.currentSlice.x, self.currentSlice.y, self.currentSlice.z)
    sphereSource.SetRadius(.05)
    #reader = vtk.vtkPNGReader()
    #reader.SetFileName(self.currentSlice.name)

    # model node
    self.model = slicer.vtkMRMLModelNode()
    self.model.SetScene(self.scene)
    self.model.SetName(self.currentSlice.name)
    self.model.SetAndObservePolyData(sphereSource.GetOutput())

    # model display node
    self.modelDisplay = slicer.vtkMRMLModelDisplayNode()
    self.modelDisplay.BackfaceCullingOff() # so plane can be seen from both front and back face
    self.modelDisplay.SetScene(self.scene)
    self.scene.AddNode(self.modelDisplay)

    # connecting model node w/ its model display node
    self.model.SetAndObserveDisplayNodeID(self.modelDisplay.GetID())

    # adding png file as texture to modelDisplay
    #self.modelDisplay.SetAndObserveTextureImageData(reader.GetOutput())
    self.scene.AddNode(self.model)

    # now doing a linear transform to set coordinates and orientation of plane
    self.transform = slicer.vtkMRMLLinearTransformNode()
    self.scene.AddNode(self.transform)
    self.model.SetAndObserveTransformNodeID(self.transform.GetID())
    vTransform = vtk.vtkTransform()
    vTransform.Scale(150, 150, 150)
    
    self.transform.SetAndObserveMatrixTransformToParent(vTransform.GetMatrix())
    
  def loadImages(self, imgFilePrefix, imageList):
    self.sliceList = []
    for name in imageList:
      self.sliceList.append(Slice(imgFilePrefix + name))
    self.currentSlice = self.sliceList[0]
    self.updateScene()
  
  def setXPosition(self, xpos):
    self.currentSlice.x = xpos
    self.updateScene()

  def setYPosition(self, ypos):
    self.currentSlice.y = ypos
    self.updateScene()
  
  def setZPosition(self, zpos):
    self.currentSlice.z = zpos
    self.updateScene()

  def setXAxisValue(self, xVal):
    # xVal and yVal must be saved in order to update slider interface when switching between image slices                                                  
    self.currentSlice.xAxisValue = xVal
    yVal = self.currentSlice.yAxisValue
                                            
    self.currentSlice.xOffset = xVal*self.currentSlice.xAxisVector[0] + yVal*self.currentSlice.yAxisVector[0]
    self.currentSlice.yOffset = xVal*self.currentSlice.xAxisVector[1] + yVal*self.currentSlice.yAxisVector[1]
    self.currentSlice.zOffset = xVal*self.currentSlice.xAxisVector[2] + yVal*self.currentSlice.yAxisVector[2]
    self.updateScene()

  def setYAxisValue(self, yVal):
    # xVal and yVal must be saved in order to update slider interface when switching between image slices                                                  
    self.currentSlice.yAxisValue = yVal
    xVal = self.currentSlice.xAxisValue
                                   
    self.currentSlice.xOffset = xVal*self.currentSlice.xAxisVector[0] + yVal*self.currentSlice.yAxisVector[0]
    self.currentSlice.yOffset = xVal*self.currentSlice.xAxisVector[1] + yVal*self.currentSlice.yAxisVector[1]
    self.currentSlice.zOffset = xVal*self.currentSlice.xAxisVector[2] + yVal*self.currentSlice.yAxisVector[2]
    self.updateScene()

  def setRotationValue(self, angle):
    self.currentSlice.planeRotation = angle
    self.updateScene()

  def setPCoords(self, coords):
    self.currentSlice.PCoordinates = coords
    self.calcAndSetNewImageCenter(coords)
    self.currentSlice.updateRotation()
    self.currentSlice.updateAxes()
    self.updateScene()
    return [self.currentSlice.x, self.currentSlice.y, self.currentSlice.z]

  def setQCoords(self, coords):
    self.currentSlice.QCoordinates = coords
    self.calcAndSetNewImageCenter(coords)
    self.currentSlice.updateRotation()
    self.currentSlice.updateAxes()
    self.updateScene()
    return [self.currentSlice.x, self.currentSlice.y, self.currentSlice.z]

  def setRCoords(self, coords):
    self.currentSlice.RCoordinates = coords
    self.calcAndSetNewImageCenter(coords)
    self.currentSlice.updateRotation()
    self.currentSlice.updateAxes()
    self.updateScene()   
    return [self.currentSlice.x, self.currentSlice.y, self.currentSlice.z]

  def setScaling(self, radius):
    self.currentSlice.radius = radius
    self.updateScene()
    
  def calcAndSetNewImageCenter(self, p):
    # New image center will be set as the point on the plane closest to the origin
    # Let the origin be defined as the point on the plane closest to the center of the 3D Slicer volume
    # http://en.wikipedia.org/wiki/Point_on_plane_closest_to_origin
    # self.currentSlice.updateRotation()
    # solving for D in plane equation:
    # a*x + b*y + c*z = d
    self.currentSlice.updateRotation()
    planeNormal = np.array(self.currentSlice.planeNormal)
    # Use updated point's coordinates for x, y, z values. Choice of point is arbitrary.
    p = np.array(p)
    d = np.dot(p, planeNormal)
    # now calculating coordinates of new center
    squaredNorm = np.dot(planeNormal, planeNormal)
    newCenterX = planeNormal[0]*d / squaredNorm
    newCenterY = planeNormal[1]*d / squaredNorm
    newCenterZ = planeNormal[2]*d / squaredNorm
    if (np.isnan(newCenterX) or np.isnan(newCenterY) or np.isnan(newCenterZ)):
      newCenterX = p[0]
      newCenterY = p[1]
      newCenterZ = p[2]
    print "The new center is: ", newCenterX, newCenterY, newCenterZ
    self.currentSlice.x = newCenterX
    self.currentSlice.y = newCenterY
    self.currentSlice.z = newCenterZ

  def updateScene(self):
    # Removing image slice that is currently in the scene.
    self.scene.RemoveNode(self.transform)
    self.scene.RemoveNode(self.modelDisplay)
    self.scene.RemoveNode(self.model)

    # Creating new nodes that represent the slice to be added in.
    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetCenter(self.currentSlice.x, self.currentSlice.y, self.currentSlice.z)
    sphereSource.SetRadius(self.currentSlice.radius)
    
    #reader = vtk.vtkPNGReader()
    #reader.SetFileName(self.currentSlice.name)
    
    # model node
    self.model = slicer.vtkMRMLModelNode()
    self.model.SetScene(self.scene)
    self.model.SetName(self.currentSlice.name)
    self.model.SetAndObservePolyData(sphereSource.GetOutput())

    # model display node
    self.modelDisplay = slicer.vtkMRMLModelDisplayNode()
    self.modelDisplay.BackfaceCullingOff() # so plane can be seen from both front and back face
    self.modelDisplay.SetScene(self.scene)
    self.scene.AddNode(self.modelDisplay)

    # connecting model node w/ its model display node
    self.model.SetAndObserveDisplayNodeID(self.modelDisplay.GetID())

    # setting image file as texture to modelDisplay
    #self.modelDisplay.SetAndObserveTextureImageData(reader.GetOutput())
    self.scene.AddNode(self.model)

    # now doing a linear transform to set coordinates and orientation of plane
    self.transform = slicer.vtkMRMLLinearTransformNode()
    self.scene.AddNode(self.transform)
    self.model.SetAndObserveTransformNodeID(self.transform.GetID())
    vTransform = vtk.vtkTransform()
    vTransform.Scale(150, 150, 150)
    
    #vTransform.Translate(self.currentSlice.xOffset, self.currentSlice.yOffset, self.currentSlice.zOffset)

    # Rotation, but still on same plane
    #vTransform.RotateWXYZ(self.currentSlice.planeRotation, *self.currentSlice.planeNormal)
    #print "The normal to the plane is ", self.currentSlice.planeNormal
    #vTransform.RotateWXYZ(self.currentSlice.rotationAngle, *self.currentSlice.rotationAxis)

    self.transform.SetAndObserveMatrixTransformToParent(vTransform.GetMatrix())

  def selectSlice(self, index):
    # This method is called when the slice index slider is changed.
    # The slice currently present in the scene is removed, and the slice located
    # at the selected index is added into the scene.
    # Positional information about the newly loaded slice is returned back
    # to the GUI so that slider values can be updated to match the slice that is
    # currently shown in the scene.
    print self.currentSlice.xAxisValue, self.currentSlice.yAxisValue
    self.currentSlice = self.sliceList[index]
    print self.currentSlice.xAxisValue, self.currentSlice.yAxisValue

    self.updateScene()
    return self.currentSlice

class Slice(object):
  def __init__(self, name=None):
    # x, y, and z coordinates for the point on plane closest to the origin
    self.x = 0
    self.y = 0
    self.z = 0
    
    # 3 points chosen by the user that define the image's alignment plane
    self.PCoordinates = [0, 0, 0]
    self.QCoordinates = [0, 0, 0]
    self.RCoordinates = [0, 0, 0]
    
    # file name of the image to be put on the slice
    if name is None:
      self.name = "default"
    else:
      self.name = name
    
    # image size scaling factor
    self.radius = 0.05

    # self.rotationAxis = [0, 0, 0]
    # self.rotationAngle = 0
    
    # normal vector to the plane
    self.planeNormal = [0, 0, 1]
    # degree of rotation of the plane around its normal
    self.planeRotation = 0
  
  def setPosition(self, x, y, z):
    self.x = x
    self.y = y
    self.z = z
  
  def setPosition(self, xyz):
    self.x = xyz[0]
    self.y = xyz[1]
    self.z = xyz[2]

  def setRadius(self, radius):
    self.radius = radius

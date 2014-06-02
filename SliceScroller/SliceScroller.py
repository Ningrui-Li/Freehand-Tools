import os
import unittest
import numpy as np
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
    self.directorySelectionButton.text = "Image Directory"
    scrollingFormLayout.addRow("Directory", self.directorySelectionButton)

    # Slice selection scroller
    self.sliceSlider = ctk.ctkSliderWidget()
    self.sliceSlider.decimals = 0
    self.sliceSlider.enabled = True
    self.sliceSlider.maximum = 2359
    scrollingFormLayout.addRow("Slices", self.sliceSlider)

    # orientation sliders
    orientationCollapsibleButton = ctk.ctkCollapsibleButton()
    orientationCollapsibleButton.text = "Orientation"
    self.layout.addWidget(orientationCollapsibleButton)
    orientationFormLayout = qt.QFormLayout(orientationCollapsibleButton)
    
    # size scaling slider
    scalingCollapsibleButton = ctk.ctkCollapsibleButton()
    scalingCollapsibleButton.text = "Image Size Scaling"
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
    
    # plane alignment point input boxes
    self.pointPCoordinateBox = ctk.ctkCoordinatesWidget()
    self.pointPCoordinateBox.dimension = 3
    self.pointPCoordinateBox.decimals = 2
    self.pointPCoordinateBox.singleStep = 0.01
    self.pointPCoordinateBox.enabled = True
    orientationFormLayout.addRow("Point P Coordinates", self.pointPCoordinateBox)

    self.pointQCoordinateBox = ctk.ctkCoordinatesWidget()
    self.pointQCoordinateBox.dimension = 3
    self.pointQCoordinateBox.decimals = 2
    self.pointQCoordinateBox.singleStep = 0.01
    orientationFormLayout.addRow("Point Q Coordinates", self.pointQCoordinateBox)

    self.pointRCoordinateBox = ctk.ctkCoordinatesWidget()
    self.pointRCoordinateBox.dimension = 3
    self.pointRCoordinateBox.decimals = 2  
    self.pointRCoordinateBox.singleStep = 0.01
    orientationFormLayout.addRow("Point R Coordinates", self.pointRCoordinateBox)
    
    # plane rotation slider
    self.rotationSlider = ctk.ctkSliderWidget()
    self.rotationSlider.decimals = 1
    self.rotationSlider.enabled = True
    self.rotationSlider.maximum = 180
    self.rotationSlider.minimum = -180
    self.rotationSlider.value = 0
    self.rotationSlider.singleStep = 0.1
    orientationFormLayout.addRow("Plane Rotation", self.rotationSlider)

    # "x-axis" and "y-axis" sliders
    self.xAxisSlider = ctk.ctkSliderWidget()  
    self.xAxisSlider.decimals = 2
    self.xAxisSlider.enabled = True
    self.xAxisSlider.maximum = 1
    self.xAxisSlider.minimum = -1
    self.xAxisSlider.value = 0
    self.xAxisSlider.singleStep = 0.01
    orientationFormLayout.addRow("X-Axis", self.xAxisSlider)
    
    self.yAxisSlider = ctk.ctkSliderWidget()  
    self.yAxisSlider.decimals = 2
    self.yAxisSlider.enabled = True
    self.yAxisSlider.maximum = 1
    self.yAxisSlider.minimum = -1
    self.yAxisSlider.value = 0
    self.yAxisSlider.singleStep = 0.01
    orientationFormLayout.addRow("Y-Axis", self.yAxisSlider)

    # image size scaling slider
    self.scalingSlider = ctk.ctkSliderWidget()
    self.scalingSlider.decimals = 0
    self.scalingSlider.enabled = True
    self.scalingSlider.maximum = 300
    self.scalingSlider.minimum = 0
    self.scalingSlider.value = 150
    scalingFormLayout.addRow("Scaling", self.scalingSlider)

    """self.console = ctk.ctkConsole()
    scalingFormLayout.addRow("Console", self.console)
    self.console.update("huehuehue")"""

    # make connections between valueChanged/coordinatesChanged signals and
    # methods that connect back to the logic.
    self.directorySelectionButton.connect('directoryChanged(QString)', self.onDirectoryChanged)
    self.sliceSlider.connect('valueChanged(double)', self.onSliderValueChanged)
    self.xSlider.connect('valueChanged(double)', self.onXPositionValueChanged)    
    self.ySlider.connect('valueChanged(double)', self.onYPositionValueChanged)    
    self.zSlider.connect('valueChanged(double)', self.onZPositionValueChanged)    
    self.pointPCoordinateBox.connect('coordinatesChanged(double*)', self.onPCoordinatesChanged)    
    self.pointQCoordinateBox.connect('coordinatesChanged(double*)', self.onQCoordinatesChanged)    
    self.pointRCoordinateBox.connect('coordinatesChanged(double*)', self.onRCoordinatesChanged)    
    self.rotationSlider.connect('valueChanged(double)', self.onRotationValueChanged)
    self.xAxisSlider.connect('valueChanged(double)', self.onXAxisValueChanged)
    self.yAxisSlider.connect('valueChanged(double)', self.onYAxisValueChanged)
    self.scalingSlider.connect('valueChanged(double)', self.onScalingValueChanged)
    
    # declare logic variable that updates image plane properties based on values passed
    # to it from the user interface
    self.logic = SliceScrollerLogic()

    # add vertical spacing
    self.layout.addStretch(1)

  # The following methods are called when a slider/coordinate value changes.
  # Slider values and coordinates and passed down, and occassionally, results are
  # returned so as to update the slider values.

  # For example, when P, Q, or R coordinates change, the center of the plane changes such that
  # it becomes the point on the plane closest to the origin.

  def onDirectoryChanged(self, value):
    print self.directorySelectionButton.directory

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
    self.scalingSlider.value = currentSlice.scaling
    
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
    # Creating list of all image slices
    sliceNameList = [i.strip() for i in open('./imageList.txt', 'r').readlines()]
    imgFilePrefix = '/luscinia/ProstateStudy/invivo/Patient59/loupas/RadialImagesCC_imwrite/'

    self.sliceList = []
    for name in sliceNameList:
      self.sliceList.append(Slice(imgFilePrefix + name))

    self.scene = slicer.mrmlScene
    self.scene.SetUndoOn()
    self.scene.SaveStateForUndo(self.scene.GetNodes())

    self.currentSlice = self.sliceList[0]

    # yay, adding images to slicer
    planeSource = vtk.vtkPlaneSource()
    planeSource.SetCenter(self.currentSlice.x, self.currentSlice.y, self.currentSlice.z)
    reader = vtk.vtkPNGReader()
    reader.SetFileName(self.currentSlice.name)

    # model node
    self.model = slicer.vtkMRMLModelNode()
    self.model.SetScene(self.scene)
    self.model.SetName(self.currentSlice.name)
    self.model.SetAndObservePolyData(planeSource.GetOutput())

    # model display node
    self.modelDisplay = slicer.vtkMRMLModelDisplayNode()
    self.modelDisplay.BackfaceCullingOff() # so plane can be seen from both front and back face
    self.modelDisplay.SetScene(self.scene)
    self.scene.AddNode(self.modelDisplay)

    # connecting model node w/ its model display node
    self.model.SetAndObserveDisplayNodeID(self.modelDisplay.GetID())

    # adding png file as texture to modelDisplay
    self.modelDisplay.SetAndObserveTextureImageData(reader.GetOutput())
    self.scene.AddNode(self.model)

    # now doing a linear transform to set coordinates and orientation of plane
    self.transform = slicer.vtkMRMLLinearTransformNode()
    self.scene.AddNode(self.transform)
    self.model.SetAndObserveTransformNodeID(self.transform.GetID())
    vTransform = vtk.vtkTransform()
    vTransform.Scale(150, 150, 150)
    
    #vTransform.RotateWXYZ(self.currentSlice.rotationAngle, *self.currentSlice.rotationAxis)

    self.transform.SetAndObserveMatrixTransformToParent(vTransform.GetMatrix())
    
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

  def setScaling(self, scaling):
    self.currentSlice.scaling = scaling
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
    planeSource = vtk.vtkPlaneSource()
    planeSource.SetCenter(self.currentSlice.x, self.currentSlice.y, self.currentSlice.z)
    planeSource.SetNormal(*self.currentSlice.planeNormal)

    reader = vtk.vtkPNGReader()
    reader.SetFileName(self.currentSlice.name)
    
    # model node
    self.model = slicer.vtkMRMLModelNode()
    self.model.SetScene(self.scene)
    self.model.SetName(self.currentSlice.name)
    self.model.SetAndObservePolyData(planeSource.GetOutput())

    # model display node
    self.modelDisplay = slicer.vtkMRMLModelDisplayNode()
    self.modelDisplay.BackfaceCullingOff() # so plane can be seen from both front and back face
    self.modelDisplay.SetScene(self.scene)
    self.scene.AddNode(self.modelDisplay)

    # connecting model node w/ its model display node
    self.model.SetAndObserveDisplayNodeID(self.modelDisplay.GetID())

    # setting image file as texture to modelDisplay
    self.modelDisplay.SetAndObserveTextureImageData(reader.GetOutput())
    self.scene.AddNode(self.model)

    # now doing a linear transform to set coordinates and orientation of plane
    self.transform = slicer.vtkMRMLLinearTransformNode()
    self.scene.AddNode(self.transform)
    self.model.SetAndObserveTransformNodeID(self.transform.GetID())
    vTransform = vtk.vtkTransform()
    vTransform.Scale(self.currentSlice.scaling, self.currentSlice.scaling, self.currentSlice.scaling)
    
    vTransform.Translate(self.currentSlice.xOffset, self.currentSlice.yOffset, self.currentSlice.zOffset)

    # Rotation, but still on same plane
    vTransform.RotateWXYZ(self.currentSlice.planeRotation, *self.currentSlice.planeNormal)
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

  # Code that was included in the template. Not used.
"""
  def hasImageData(self,volumeNode):
    """"""This is a dummy logic method that 
    returns true if the passed in volume
    node has valid image data""""""
    if not volumeNode:
      print('no volume node')
      return False
    if volumeNode.GetImageData() == None:
      print('no image data')
      return False
    return True

  def delayDisplay(self,message,msec=1000):
    #
    # logic version of delay display
    #
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    self.delayDisplay(description)

    if self.enableScreenshots == 0:
      return

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == -1:
      # full window
      widget = slicer.util.mainWindow()
    elif type == slicer.qMRMLScreenShotDialog().FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog().ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog().Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog().Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog().Green:
      # green slice window
      widget = lm.sliceWidget("Green")

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, self.screenshotScaleFactor, imageData)

  def run(self,inputVolume,outputVolume,enableScreenshots=0,screenshotScaleFactor=1):
    """"""Run the actual algorithm""""""

    self.delayDisplay('Running the algorithm')

    self.enableScreenshots = enableScreenshots
    self.screenshotScaleFactor = screenshotScaleFactor

    self.takeScreenshot('VolumeScroller-Start','Start',-1)

    return True
"""

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
    self.scaling = 150

    # self.rotationAxis = [0, 0, 0]
    # self.rotationAngle = 0
    
    # normal vector to the plane
    self.planeNormal = [0, 0, 1]
    # degree of rotation of the plane around its normal
    self.planeRotation = 0

    # when the image is rotated in space and aligned on a new plane,
    # it is beneficial to be able to translate it around while still having
    # it bound to its alignment plane.
    # these vectors give directions for moving the image plane
    # along the newly-defined "x-axis" and "y-axis".
    self.xAxisVector = [1, 0, 0]
    self.yAxisVector = [0, 1, 0]

    # These are offset values for the image from the point on
    # the plane closest to the origin.
    # Offsets of all zero mean that the image plane is centered
    # on the point on the plane closest to the origin.
    self.xAxisValue = 0
    self.yAxisValue = 0
    self.xOffset = 0
    self.yOffset = 0
    self.zOffset = 0
  
  def setPosition(self, x, y, z):
    self.x = x
    self.y = y
    self.z = z
  
  def setPosition(self, xyz):
    self.x = xyz[0]
    self.y = xyz[1]
    self.z = xyz[2]

  """def setAngles(self, xAng, yAng, zAng):
    self.xAngle = xAng
    self.yAngle = yAng
    self.zAngle = zAng

  def setAngles(self, xyzAng):
    self.xAngle = xyzAng[0]
    self.yAngle = xyzAng[1]
    self.zAngle = xyzAng[2]
    """

  def setScaling(self, scaling):
    self.scaling = scaling

  def updateRotation(self):
    # This function is called when the coordinates of any of the three points
    # P, Q, or R change. Changing any of the three points means that a new
    # plane normal will have to be calculated for the slice. This is done
    # by taking the cross product of any two direction vectors constructed using
    # P, Q, or R.
    p = np.array(self.PCoordinates)
    q = np.array(self.QCoordinates)
    r = np.array(self.RCoordinates)
    # calculating direction vectors PQ and PR, then taking their cross product
    # to acquire normal to the newly defined plane 
    pq = np.subtract(q, p)
    pr = np.subtract(r, p)
    self.planeNormal = np.cross(pq, pr)
    #print self.planeNormal

    # take cross product of normal of user-defined plane and 
    # default plane (0 0 1) to get axis of rotation
    #originalNormal = np.array([0, 0, 1])
    #self.rotationAxis = np.cross(self.planeNormal, originalNormal)

    # now use dot product definition to calculate angle of rotation
    # dot product: A (dot) B = |A|*|B|*cos(angle)
    #newPlaneNormalLength = np.sqrt(self.planeNormal[0]**2 + self.planeNormal[1]**2 + self.planeNormal[2]**2
    #self.rotationAngle = np.arccos(np.dot(self.planeNormal, originalNormal) / newPlaneNormalLength) # in radians
    #self.rotationAngle = self.rotationAngle * 180/np.pi # conversion to degrees
    #print "Rotation Angle is now", self.rotationAngle
    #print "Rotation Axis is now", self.rotationAxis

  def updateAxes(self):
    # Let plane normal be the vector (a, b, c)
    planeNormal = np.array(self.planeNormal)
    # Checking to see if (c, c, -a-b) is a valid perpendicular vector
    if (planeNormal[2] == 0) and (-planeNormal[0]-planeNormal[1] == 0):
      # (c, c, -a-b) is invalid since it's the zero vector, so choose (-b-c, a, a)
      self.xAxisVector = np.array([-planeNormal[1]-planeNormal[2], planeNormal[0], planeNormal[0]])
    else:
      # (c, c, -a-b) is valid (nonzero), so choose (c, c, -a-b)
      self.xAxisVector = np.array([planeNormal[2], planeNormal[2], -planeNormal[0]-planeNormal[1]])
    # y-axis vector must be perpendicular to the plane normal and the newly calculated x-axis vector
    self.yAxisVector = np.cross(planeNormal, self.xAxisVector)

    # normalizing to unit vectors
    xAxisLength = np.sqrt(np.dot(self.xAxisVector, self.xAxisVector))
    yAxisLength = np.sqrt(np.dot(self.yAxisVector, self.yAxisVector))
    self.xAxisVector = np.divide(self.xAxisVector, xAxisLength)
    self.yAxisVector = np.divide(self.yAxisVector, yAxisLength)

    print "My x is %f %f %f" % (self.xAxisVector[0], self.xAxisVector[1], self.xAxisVector[2])
    print "My y is %f %f %f" % (self.yAxisVector[0], self.yAxisVector[1], self.yAxisVector[2]) 

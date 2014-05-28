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

    # Slice selection scroller
    self.slider = ctk.ctkSliderWidget()
    self.slider.decimals = 0
    self.slider.enabled = True
    scrollingFormLayout.addRow("Slices", self.slider)

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

    # x, y, z center sliders
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

    """self.zSlider = ctk.ctkSliderWidget()
    self.zSlider.decimals = 2
    self.zSlider.enabled = True
    self.zSlider.maximum = 1
    self.zSlider.minimum = -1
    self.zSlider.value = 0
    self.zSlider.singleStep = 0.01
    orientationFormLayout.addRow("Center - Z Position", self.zSlider)"""

    # euler angle orientation sliders
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

    # image size scaling slider
    self.scalingSlider = ctk.ctkSliderWidget()
    self.scalingSlider.decimals = 0
    self.scalingSlider.enabled = True
    self.scalingSlider.maximum = 300
    self.scalingSlider.minimum = 0
    self.scalingSlider.value = 150
    scalingFormLayout.addRow("Scaling", self.scalingSlider)

    # make connections
    self.slider.connect('valueChanged(double)', self.onSliderValueChanged)
    self.xSlider.connect('valueChanged(double)', self.onXPositionValueChanged)    
    self.ySlider.connect('valueChanged(double)', self.onYPositionValueChanged)    
    #self.zSlider.connect('valueChanged(double)', self.onZPositionValueChanged)    
    self.pointPCoordinateBox.connect('coordinatesChanged(double*)', self.onPCoordinatesChanged)    
    self.pointQCoordinateBox.connect('coordinatesChanged(double*)', self.onQCoordinatesChanged)    
    self.pointRCoordinateBox.connect('coordinatesChanged(double*)', self.onRCoordinatesChanged)    
    self.scalingSlider.connect('valueChanged(double)', self.onScalingValueChanged)
    
    self.logic = SliceScrollerLogic()

    # add vertical spacing
    self.layout.addStretch(1)

  def onSliderValueChanged(self, value):
    self.logic.selectSlice(int(value))

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
    self.logic.setPCoords(coords)

  def onQCoordinatesChanged(self, value):
    coords = [float(x) for x in self.pointQCoordinateBox.coordinates.split(',')]
    self.logic.setQCoords(coords)

  def onRCoordinatesChanged(self, value):
    coords = [float(x) for x in self.pointRCoordinateBox.coordinates.split(',')]
    self.logic.setRCoords(coords)

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
    self.scene = slicer.mrmlScene
    self.currentSlice = Slice('/luscinia/ProstateStudy/invivo/Patient59/loupas/RadialImagesCC_imwrite/arfi_ts3_26.57.png')

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
    
    vTransform.RotateWXYZ(self.currentSlice.rotationAngle, *self.currentSlice.rotationAxis)

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

  def setPCoords(self, coords):
    self.currentSlice.PCoordinates = coords
    newCenter = self.calcNewImageCenter(coords)
    self.updatePlaneOffset(coords)
    self.currentSlice.updateRotation()
    self.updateScene()

  def setQCoords(self, coords):
    self.currentSlice.QCoordinates = coords
    newCenter = self.calcNewImageCenter(coords)
    self.updatePlaneOffset(coords)
    self.currentSlice.updateRotation()
    self.updateScene()

  def setRCoords(self, coords):
    self.currentSlice.RCoordinates = coords
    newCenter = self.calcNewImageCenter(coords)
    self.updatePlaneOffset(coords)
    self.currentSlice.updateRotation()
    self.updateScene()

  def setScaling(self, scaling):
    self.currentSlice.scaling = scaling
    self.updateScene()

  def updatePlaneOffset(self, coords):
    self.scene.RemoveNode(self.transform)
    self.scene.RemoveNode(self.modelDisplay)
    self.scene.RemoveNode(self.model)

    planeSource = vtk.vtkPlaneSource()
    planeSource.SetCenter(coords[0], coords[1], coords[2])
    self.currentSlice.x = coords[0]
    self.currentSlice.y = coords[1]
    self.currentSlice.z = coords[2]
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

    # adding tiff file as texture to modelDisplay
    self.modelDisplay.SetAndObserveTextureImageData(reader.GetOutput())
    self.scene.AddNode(self.model)

    # now doing a linear transform to set coordinates and orientation of plane
    self.transform = slicer.vtkMRMLLinearTransformNode()
    self.scene.AddNode(self.transform)
    self.model.SetAndObserveTransformNodeID(self.transform.GetID())
    vTransform = vtk.vtkTransform()
    vTransform.Scale(self.currentSlice.scaling, self.currentSlice.scaling, self.currentSlice.scaling)
    vTransform.RotateWXYZ(0, *self.currentSlice.rotationAxis)
    self.transform.SetAndObserveMatrixTransformToParent(vTransform.GetMatrix())
    
  def calcNewImageCenter(self, p):
    # New image center will be set as the point on the plane closest to the origin
    # Let the origin be defined as the point on the plane closest to the center of the 3D Slicer volume
    # http://en.wikipedia.org/wiki/Point_on_plane_closest_to_origin

    self.currentSlice.updateRotation()
    # solving for D in plane equation:
    # a*x + b*y + c*z + d = 0
    p = np.array(self.currentSlice.PCoordinates)
    planeNormal = np.array(self.currentSlice.rotationAxis)
    # Use updated point's coordinates for x, y, z values. Choice of point is arbitrary.
    d = -1 * np.dot(p, planeNormal)
    # now calculating coordinates of new center
    squaredNorm = np.dot(p, p)
    newCenterX = p[0]*d / squaredNorm
    newCenterY = p[1]*d / squaredNorm
    newCenterZ = p[2]*d / squaredNorm
    return [newCenterX, newCenterY, newCenterZ]

  def updateScene(self):
    self.scene.RemoveNode(self.transform)
    self.scene.RemoveNode(self.modelDisplay)
    self.scene.RemoveNode(self.model)

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

    # adding tiff file as texture to modelDisplay
    self.modelDisplay.SetAndObserveTextureImageData(reader.GetOutput())
    self.scene.AddNode(self.model)

    # now doing a linear transform to set coordinates and orientation of plane
    self.transform = slicer.vtkMRMLLinearTransformNode()
    self.scene.AddNode(self.transform)
    self.model.SetAndObserveTransformNodeID(self.transform.GetID())
    vTransform = vtk.vtkTransform()
    vTransform.Scale(self.currentSlice.scaling, self.currentSlice.scaling, self.currentSlice.scaling)
    vTransform.RotateWXYZ(self.currentSlice.rotationAngle, *self.currentSlice.rotationAxis)
    self.transform.SetAndObserveMatrixTransformToParent(vTransform.GetMatrix())
    
  def selectSlice(self, index):
    self.scene.Undo()
    self.scene.SaveStateForUndo(self.scene.GetNodes())
    imgFilePrefix = './data/test'
    imgFileSuffix = '.tiff'
    # yay, adding images to slicer
    planeSource = vtk.vtkPlaneSource()

    reader = vtk.vtkTIFFReader()
    reader.SetFileName(imgFilePrefix + str(self.imageList[index]) + imgFileSuffix)
    #reader.CanReadFile('imgFilePrefix + str(self.imageList[0]) + imgFileSuffix')

    # model node
    model = slicer.vtkMRMLModelNode()
    model.SetScene(self.scene)
    model.SetName("test " + str(self.imageList[index]) + "cow")
    model.SetAndObservePolyData(planeSource.GetOutput())

    # model display node
    modelDisplay = slicer.vtkMRMLModelDisplayNode()
    modelDisplay.BackfaceCullingOff() # so plane can be seen from both front and back face
    modelDisplay.SetScene(self.scene)
    self.scene.AddNode(modelDisplay)

    # connecting model node w/ its model display node
    model.SetAndObserveDisplayNodeID(modelDisplay.GetID())

    # adding tiff file as texture to modelDisplay
    modelDisplay.SetAndObserveTextureImageData(reader.GetOutput())
    self.scene.AddNode(model)

    # now doing a linear transform to set coordinates and orientation of plane
    transform = slicer.vtkMRMLLinearTransformNode()
    self.scene.AddNode(transform)
    model.SetAndObserveTransformNodeID(transform.GetID())
    vTransform = vtk.vtkTransform()
    vTransform.Scale(150, 150, 150)
    vTransform.RotateX(self.rotateXList[index])
    vTransform.RotateY(self.rotateYList[index])
    vTransform.RotateZ(self.rotateZList[index])

    transform.SetAndObserveMatrixTransformToParent(vTransform.GetMatrix())

  def hasImageData(self,volumeNode):
    """This is a dummy logic method that 
    returns true if the passed in volume
    node has valid image data"""
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
    """Run the actual algorithm"""

    self.delayDisplay('Running the algorithm')

    self.enableScreenshots = enableScreenshots
    self.screenshotScaleFactor = screenshotScaleFactor

    self.takeScreenshot('VolumeScroller-Start','Start',-1)

    return True

class Slice(object):
  def __init__(self, name=None):
    self.x = 0
    self.y = 0
    self.z = 0
    self.PCoordinates = [0, 0, 0]
    self.QCoordinates = [0, 0, 0]
    self.RCoordinates = [0, 0, 0]
    if name is None:
      self.name = "default"
    else:
      self.name = name
    self.scaling = 150
    self.rotationAxis = [0, 0, 1]
    self.rotationAngle = 0
  
  def setPosition(self, x, y, z):
    self.x = x
    self.y = y
    self.z = z
  
  def setPosition(self, xyz):
    self.x = xyz[0]
    self.y = xyz[1]
    self.z = xyz[2]

  def setAngles(self, xAng, yAng, zAng):
    self.xAngle = xAng
    self.yAngle = yAng
    self.zAngle = zAng

  def setAngles(self, xyzAng):
    self.xAngle = xyzAng[0]
    self.yAngle = xyzAng[1]
    self.zAngle = xyzAng[2]

  def setScaling(self, scaling):
    self.scaling = scaling

  def updateRotation(self):
    p = np.array(self.PCoordinates)
    q = np.array(self.QCoordinates)
    r = np.array(self.RCoordinates)
    # calculating vectors pq and pr, then taking their cross product
    # to acquire normal to the new, user-defined plane 
    pq = np.subtract(q, p)
    pr = np.subtract(r, p)
    newPlaneNormal = np.cross(pq, pr)
    # take cross product of normal of user-defined plane and 
    # default plane (0 0 1) to get axis of rotation
    originalNormal = np.array([0, 0, 1])
    self.rotationAxis = np.cross(newPlaneNormal, originalNormal)
    # now use dot product definition to calculate angle of rotation
    # dot product: A (dot) B = |A|*|B|*cos(angle)
    newPlaneNormalLength = np.sqrt(newPlaneNormal[0]**2 + newPlaneNormal[1]**2 + newPlaneNormal[2]**2)
    self.rotationAngle = np.arccos(np.dot(newPlaneNormal, originalNormal) / newPlaneNormalLength) # in radians
    self.rotationAngle = self.rotationAngle * 180/np.pi # conversion to degrees
    #print "Rotation Angle is now", self.rotationAngle
    #print "Rotation Axis is now", self.rotationAxis

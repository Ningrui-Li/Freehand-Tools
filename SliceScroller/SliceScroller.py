import os
import unittest
from __main__ import vtk, qt, ctk, slicer

class SliceScroller(object):
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

class SliceScrollerWidget(object):
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

    self.zSlider = ctk.ctkSliderWidget()
    self.zSlider.decimals = 2
    self.zSlider.enabled = True
    self.zSlider.maximum = 1
    self.zSlider.minimum = -1
    self.zSlider.value = 0
    self.zSlider.singleStep = 0.01
    orientationFormLayout.addRow("Center - Z Position", self.zSlider)

    # euler angle orientation sliders

    self.xAngleSlider = ctk.ctkSliderWidget()
    self.xAngleSlider.decimals = 1
    self.xAngleSlider.enabled = True
    self.xAngleSlider.maximum = 180
    self.xAngleSlider.minimum = -180
    self.xAngleSlider.value = 0
    self.xAngleSlider.singleStep = 0.1
    orientationFormLayout.addRow("X Angle", self.xAngleSlider)

    self.yAngleSlider = ctk.ctkSliderWidget()
    self.yAngleSlider.decimals = 1
    self.yAngleSlider.enabled = True
    self.yAngleSlider.maximum = 180
    self.yAngleSlider.minimum = -180
    self.yAngleSlider.value = 0
    self.yAngleSlider.singleStep = 0.1
    orientationFormLayout.addRow("Y Angle", self.yAngleSlider)

    self.zAngleSlider = ctk.ctkSliderWidget()
    self.zAngleSlider.decimals = 1
    self.zAngleSlider.enabled = True
    self.zAngleSlider.maximum = 180
    self.zAngleSlider.minimum = -180
    self.zAngleSlider.value = 0
    self.zAngleSlider.singleStep = 0.1
    orientationFormLayout.addRow("Z Angle", self.zAngleSlider)

    # image size scaling slider
    self.scalingSlider = ctk.ctkSliderWidget()
    self.scalingSlider.decimals = 0
    self.scalingSlider.enabled = True
    self.scalingSlider.maximum = 300
    self.scalingSlider.minimum = 0
    self.scalingSlider.value = 150
    scalingFormLayout.addRow("Scaling", self.scalingSlider)

    # refresh button
    # self.refreshButton = qt.QPushButton("Refresh")
    # orientationFormLayout.addRow(self.refreshButton)

    # make connections
    self.slider.connect('valueChanged(double)', self.onSliderValueChanged)
    self.xSlider.connect('valueChanged(double)', self.onXPositionValueChanged)    
    self.ySlider.connect('valueChanged(double)', self.onYPositionValueChanged)    
    self.zSlider.connect('valueChanged(double)', self.onZPositionValueChanged)    
    self.xAngleSlider.connect('valueChanged(double)', self.onXAngleValueChanged)    
    self.yAngleSlider.connect('valueChanged(double)', self.onYAngleValueChanged)    
    self.zAngleSlider.connect('valueChanged(double)', self.onZAngleValueChanged)    
    self.scalingSlider.connect('valueChanged(double)', self.onScalingValueChanged)
    #self.refreshButton.connect('clicked()', self.onRefresh)
    
    self.logic = SliceScrollerLogic()
    # call refresh on the slider to set its initial state
    #self.onRefresh()

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

  def onXAngleValueChanged(self, value):
    self.logic.setXAngle(value)

  def onYAngleValueChanged(self, value):
    self.logic.setYAngle(value)

  def onZAngleValueChanged(self, value):
    self.logic.setZAngle(value)
  
  def onScalingValueChanged(self, value):
    self.logic.setScaling(value)

  # def onRefresh(self):
  #  self.slider.maximum = 4 

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

class SliceScrollerLogic(object):
  """This class should implement all the actual 
  computation done by your module.  The interface 
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    self.scene = slicer.mrmlScene
    self.scene.SetUndoOn()
    self.scene.SaveStateForUndo(self.scene.GetNodes())
    
    self.currentSlice = Slice('/luscinia/ProstateStudy/invivo/Patient59/loupas/RadialImagesCC_imwrite/arfi_ts3_26.57.png')

    # yay, adding images to slicer
    planeSource = vtk.vtkPlaneSource()
    planeSource.SetCenter(self.currentSlice.x, self.currentSlice.y, self.currentSlice.z)
    reader = vtk.vtkPNGReader()
    reader.SetFileName(self.currentSlice.name)

    # model node
    model = slicer.vtkMRMLModelNode()
    model.SetScene(self.scene)
    model.SetName(self.currentSlice.name)
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
    vTransform.RotateX(0)
    vTransform.RotateY(0)
    vTransform.RotateZ(0)

    transform.SetAndObserveMatrixTransformToParent(vTransform.GetMatrix())
  
  def setXPosition(self, xpos):
    self.currentSlice.x = xpos
    self.updateScene()

  def setYPosition(self, ypos):
    self.currentSlice.y = ypos
    self.updateScene()
  
  def setZPosition(self, zpos):
    self.currentSlice.z = zpos
    self.updateScene()

  def setXAngle(self, xpos):
    self.currentSlice.xAngle = xpos
    self.updateScene()

  def setYAngle(self, ypos):
    self.currentSlice.yAngle = ypos
    self.updateScene()
  
  def setZAngle(self, zpos):
    self.currentSlice.zAngle = zpos
    self.updateScene()

  def setScaling(self, scaling):
    self.currentSlice.scaling = scaling
    self.updateScene()

  def updateScene(self):
    self.scene.Undo()
    self.scene.SaveStateForUndo(self.scene.GetNodes())

    planeSource = vtk.vtkPlaneSource()
    planeSource.SetCenter(self.currentSlice.x, self.currentSlice.y, self.currentSlice.z)
    reader = vtk.vtkPNGReader()
    reader.SetFileName(self.currentSlice.name)

    # model node
    model = slicer.vtkMRMLModelNode()
    model.SetScene(self.scene)
    model.SetName(self.currentSlice.name)
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
    vTransform.Scale(self.currentSlice.scaling, self.currentSlice.scaling, self.currentSlice.scaling)
    vTransform.RotateX(self.currentSlice.xAngle)
    vTransform.RotateY(self.currentSlice.yAngle)
    vTransform.RotateZ(self.currentSlice.zAngle)
    transform.SetAndObserveMatrixTransformToParent(vTransform.GetMatrix())
    
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
    self.xAngle = 0
    self.yAngle = 0
    self.zAngle = 0
    if name is None:
      self.name = "default"
    else:
      self.name = name
    self.scaling = 150
  
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

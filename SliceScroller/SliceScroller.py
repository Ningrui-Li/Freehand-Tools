import os
import unittest
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
    parent.acknowledgementText = """
    zzzzzzzzzzzzzzzz
""" # replace with organization, grant and thanks.
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

    # refresh button
    self.refreshButton = qt.QPushButton("Refresh")
    scrollingFormLayout.addRow(self.refreshButton)

    # make connections
    self.slider.connect('valueChanged(double)', self.onSliderValueChanged)
    self.refreshButton.connect('clicked()', self.onRefresh)
    
    self.logic = SliceScrollerLogic()
    # call refresh on the slider to set its initial state
    self.onRefresh()

    # add vertical spacing
    self.layout.addStretch(1)

  def onSliderValueChanged(self, value):
    self.logic.selectSlice(int(value))

  def onRefresh(self):
    self.slider.maximum = 4 

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
    self.scene.SetUndoOn()
    self.scene.SaveStateForUndo(self.scene.GetNodes())
    
    # HARD-CODED TEST VALUES
    imgFilePrefix = './data/test'
    imgFileSuffix = '.tiff'
    self.imageList = range(1, 6)
    self.rotateXList = [30, 60, 90, 120, 150]
    self.rotateYList = [15, 30, 45, 60, 75]
    self.rotateZList = [10, 20, 30, 40, 50]

    # yay, adding images to slicer
    planeSource = vtk.vtkPlaneSource()

    reader = vtk.vtkTIFFReader()
    reader.SetFileName(imgFilePrefix + str(self.imageList[0]) + imgFileSuffix)
    #reader.CanReadFile('imgFilePrefix + str(self.imageList[0]) + imgFileSuffix')

    # model node
    model = slicer.vtkMRMLModelNode()
    model.SetScene(self.scene)
    model.SetName("test " + str(self.imageList[0]) + "cow")
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
    vTransform.Scale(300, 300, 300)
    vTransform.RotateX(self.rotateXList[0])
    vTransform.RotateY(self.rotateYList[0])
    vTransform.RotateZ(self.rotateZList[0])

    transform.SetAndObserveMatrixTransformToParent(vTransform.GetMatrix())
  
  def selectSlice(self, index):
    self.scene.Undo()
    self.scene.SaveStateForUndo(self.scene.GetNodes())
    imgFilePrefix = './data/test'
    imgFileSuffix = '.tiff'
    # yay, adding images to slicer
    planeSource = vtk.vtkPlaneSource()

    # Possible useful future command for plane offset from origin

    #planeSource.SetCenter(.5, 0, 0)

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
    vTransform.Scale(300, 300, 300)
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

    self.delayDisplay('Running the aglorithm')

    self.enableScreenshots = enableScreenshots
    self.screenshotScaleFactor = screenshotScaleFactor

    self.takeScreenshot('VolumeScroller-Start','Start',-1)

    return True


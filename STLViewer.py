#!/usr/bin/env python3
import sys
import os

import vtk
import numpy
import cv2
    
# TODO: rotate model does not work nicely if up axis was wrong

################################################
### Print Manual
################################################
print ("STLViewer v0.1 (python3)")
print ("")
print ("Arguments: no arguments will open current dir and default size")
print ("           valid arguments: 'file:[yourfile.stl]' OR 'dir:[yourdir]'")
print ("                            'size:[width],[height]' for windowsize" )
print ("                            'auto' to autoscan dir and save png's" )
print ("")
print ("Controls: [mouse-left]: rotate, [mouse-wheel/right]: zoom, ")
print ("          [up]: change up vector, [down]: rotate model")
print ("          [s]: shrink to fit, [g]: grow to fit")
print ("          [space]: save screenshot, [q],[esc]: quit viewer")
print ("")

################################################
### GET all input values like filepath and derive working dir
################################################

filename='.'
argsList=sys.argv[1:]

# Get dir where we show files from
filepath=os.getcwd()
for arg in argsList:
  if 'dir:' in arg:
    key,val=arg.split(':')
    if not os.path.isdir(val):
      print ("Directory is not a valid path")
      quit()
    filepath=os.path.abspath(val)
  if 'file:' in arg:
    key,val=arg.split(':')
    if not os.path.isfile(val):
      print ("File is not found")
      quit()
    absfilename=os.path.abspath(val)
    filepath=os.path.split(absfilename)[0]

# Get STL files in found dir
otherfiles=[]
for file in os.listdir(filepath):  
    name, ext = os.path.splitext(file)
    if ext.lower()==".stl":
      otherfiles.append(file)  
otherfiles=sorted(otherfiles,key=str.lower)
last_idx=len(otherfiles)-1

# Check if files in dir
if len(otherfiles)==0:
      print ("No STL files found to display.")
      quit()

# Check if file key used
idx=0
for arg in argsList:
  if 'file:' in arg:
    filename=arg.split(':')[1]
    idx=otherfiles.index(os.path.split(filename)[1])

# Extract window size if specified
w,h=240,240
for arg in argsList:
  if 'size:' in arg:
    size=arg.split(':')[1].split(',')
    if len(size)!=2:
      print ("'size' value should have format 'width,height', e.g. '320,240'.")
      quit()
    w,h=int(size[0]),int(size[1])

# Check if we are in automatic screenshot mode
auto=False
for arg in argsList:
  if 'auto' in arg:
    auto=True

###################################################

print ("Load init file - idx:",idx,otherfiles[idx])
nfilename=otherfiles[idx]

def growImage():
    global campos,camfoc,camup,camera,ren,renWin

    while isFitImage():
      campos[0]=campos[0]/1.1
      campos[1]=campos[1]/1.1
      camera=vtk.vtkCamera()
      camera.SetViewUp(camup)
      camera.SetFocalPoint(camfoc)
      camera.SetPosition(campos)
      ren.SetActiveCamera(camera)
      renWin.Render()
    fitImage()

def fitImage():
    global campos,camfoc,camup,camera,ren,renWin

    while not isFitImage():
      campos[0]=campos[0]*1.1
      campos[1]=campos[1]*1.1
      camera=vtk.vtkCamera()
      camera.SetViewUp(camup)
      camera.SetFocalPoint(camfoc)
      camera.SetPosition(campos)
      ren.SetActiveCamera(camera)
      renWin.Render()

def isFitImage():
    global vtk,renWin,idx,nfilename,w,h
    #print ("fitImage",idx,filename) 
    image = vtk.vtkWindowToImageFilter()
    image.SetInput(renWin)
    image.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetWriteToMemory(1)
    writer.SetInputConnection(image.GetOutputPort())
    writer.Write()
    
    shape=image.GetOutput().GetDimensions()
    assert shape[2]==1, "Expected 3d dimension to be 1!"
    shape=shape[:2]    
    bpp=image.GetOutput().GetScalarSize()
    assert bpp==1, "Expected png image with pixeldata in numpy.uint8!"
    #print ("Shape:",shape)
    #print ("Bytes per pixel",bpp)
    
    data=numpy.frombuffer(writer.GetResult(),dtype=numpy.uint8)
    #print ("data",data.shape,data.dtype)#,data)
    im=cv2.imdecode(data,cv2.IMREAD_UNCHANGED)
    #print ("im",im.shape,im.dtype)#,data)
    fit=True
    R,G,B=2,1,0
    for x in range(0,w):
      blackTop=not numpy.any(im[0,x,:])
      blackBot=not numpy.any(im[h-1,x,:])
      if not blackTop or not blackBot: fit=False
    for y in range(0,h):
      blackLeft=not numpy.any(im[y,0,:])
      blackRight=not numpy.any(im[y,w-1,:])
      if not blackLeft or not blackRight: fit=False
    #cv2.imwrite("test.png",im)

    return fit

def makePrintScreen():
    global vtk,renWin,idx,nfilename
    image = vtk.vtkWindowToImageFilter()
    image.SetInput(renWin)
    image.Update()
    writer = vtk.vtkPNGWriter()
    barename, ext = os.path.splitext(nfilename)
    imgname=os.path.join(filepath,barename+".png")
    writer.SetFileName(imgname)
    writer.SetInputData(image.GetOutput())
    writer.Write()  

camIdx=0
camUp=[(0,1,0),(1,0,0),(0,0,1),(0,-1,0),(-1,0,0),(0,0,-1)]
camDirIdx=0
def keypress_callback(obj, ev):
    global idx,nfilename,reader,renWin,ren,camPos,camIdx
    key = obj.GetKeySym()

    if key=='KP_Left' or key=='Left': 
      idx=idx-1
      if idx<0: 
        idx=0
      else:  
        nfilename=otherfiles[idx]
        #reader.SetFileName(nfilename)
        loadFile()
        print ("Load prev file - idx:",idx,nfilename)
    if key=='KP_Right' or key=='Right':
      idx=idx+1
      if idx>last_idx: 
        idx=last_idx
      else:  
        nfilename=otherfiles[idx]
        #reader.SetFileName(nfilename)
        loadFile()
        print ("Load next file - idx:",idx,nfilename)
    if key=='space': 
      print ("Save print screen of ",idx,nfilename) 
      makePrintScreen()
    if key=='Escape': quit()
    if key=='s':
      print ("Shrink to fit image")
      fitImage()
    if key=='g':
      print ("Grow to fit image")
      growImage()
    if key=='KP_Up' or key=="Up":
      print ("Change up vector")
      global campos,camfoc,camup,camera,ren,renWin
      global camUp,camIdx
      camIdx=camIdx+1
      if camIdx>5: camIdx=0
      if camIdx<0: camIdx=5
      camup=camUp[camIdx]
      camera=vtk.vtkCamera()
      camera.SetViewUp(camup)
      camera.SetFocalPoint(camfoc)
      camera.SetPosition(campos)
      ren.SetActiveCamera(camera)
      renWin.Render()           
    if key=='KP_Down' or key=="Down":
      global camDirIdx
      camDirIdx=camDirIdx+1
      if camDirIdx>3: camDirIdx=0
      if camDirIdx==1: campos[1]=-campos[1]
      if camDirIdx==2: campos[0]=-campos[0]
      if camDirIdx==3: campos[1]=-campos[1]
      if camDirIdx==0: campos[0]=-campos[0]
      camera=vtk.vtkCamera()
      camera.SetViewUp(camup)
      camera.SetFocalPoint(camfoc)
      camera.SetPosition(campos)
      ren.SetActiveCamera(camera)
      renWin.Render()           

campos=[0,0,0]    
camfoc=[0,0,0]
camup=[0,0,0]
camera=None
def loadFile():
  
    global actor,nfilename,vtk,ren,reader,iren, renWin,loading
    global camera,campos,camfoc,camup
    if loading: return

    loading=True
    ren.SetBackground(1,0,0)
    renWin.Render()
    renWin.SetWindowName("STLViewer - loading...")

    reader = vtk.vtkSTLReader()
    reader.SetFileName(os.path.join(filepath,nfilename))
    
    mapper = vtk.vtkPolyDataMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        mapper.SetInput(reader.GetOutput())
    else:
        mapper.SetInputConnection(reader.GetOutputPort())

    renWin.RemoveRenderer(ren)
    ren = vtk.vtkRenderer()
    renWin.AddRenderer(ren)

    ren.RemoveActor(actor)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    ren.AddActor(actor)
    #iren.Initialize()
    
    addText("")

    # Set camera up
    #camera=ren.GetActiveCamera()
    bnds=actor.GetBounds()
    mZ=(bnds[5]+bnds[4])/2
    mX=(bnds[1]+bnds[0])/2
    mY=(bnds[3]+bnds[2])/2
    dX=bnds[1]-bnds[0]
    dY=bnds[3]-bnds[2]
    dZ=bnds[5]-bnds[4]
    #sC=1.5*max(dY,dZ)+1.75*dX
    sC=1.4*dZ
    #print ('%.2f' % dX,'%.2f' % dY,'%.2f' % dZ,"->",'%.2f' % sC)
    #changeText(str())

    camera=vtk.vtkCamera()
    camera.SetViewUp(0,0,1)
    camera.SetFocalPoint(mX,mY,mZ)
    camup=[0,0,1]
    camfoc=[mX,mY,mZ]
    #sC is not enough, a fatter object is closer to the cam.
    #camera.SetPosition(sC+2.5*dX/2,0,mZ)
    campos=[sC,-sC,mZ]
    camera.SetPosition(campos)
    #print (camera.GetOrientation())
    ren.SetActiveCamera(camera)

    fitImage()

    renWin.SetWindowName("STLViewer - "+nfilename.split('.')[-2])
    ren.SetBackground(0,0,0)
    renWin.Render()

    loading=False

# Create a rendering window and renderer
renWin = vtk.vtkRenderWindow()
renWin.SetWindowName("STLViewer")
renWin.SetSize(w,h)
ren = vtk.vtkRenderer()
reader=None;

# Create a debug message actor
txt=None
def addText(msg="Hello world!"):
  global txt
  txt = vtk.vtkTextActor()
  txt.SetInput(msg)
  txtprop=txt.GetTextProperty()
  txtprop.SetFontFamilyToArial()
  txtprop.SetFontSize(18)
  txtprop.SetColor(250,1,1)
  txt.SetDisplayPosition(10,10)
  ren.AddActor(txt)
def changeText(msg="New text!"):
  global txt
  txt.SetInput(msg)

# Create a renderwindowinteractor
iren = vtk.vtkRenderWindowInteractor()
iren.AddObserver('KeyPressEvent', keypress_callback, 1.0)
iren.SetRenderWindow(renWin)


# Assign actor to the renderer
actor=None

if auto:
  iren.Initialize()
  for idx in range(0,last_idx):
    nfilename=otherfiles[idx]
    loading=False
    loadFile()
    makePrintScreen()
  quit()
else:
  loading=False
  loadFile()

  # Enable user interface interactor
  iren.Initialize()
  renWin.Render()
  iren.Start()

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
print ("Usage: STLViewer.py file:'yourfile.stl' optionalkey:value")
print ("       Valid optional keys are 'auto':None,'size':width,height")
print ("       If no arguments present, first STL will be loaded")
print ("")
print ("Controls: [mouse-left]: rotate, [mouse-wheel/right]: zoom, ")
print ("          [up]: change up vector, [down]: save screenshot")
print ("          [up]: change up vector, [space]: save screenshot")
print ("          [a]: shrink to fit screen, [q],[esc]: quit viewer")
print ("")

################################################
### GET all input values like filepath and derive working dir
################################################

filename='.'
argsList=sys.argv[1:]

# If we have not command line arguments we display all stl files (if present)
otherfiles=[]
if len(argsList)==0:
  filepath=os.getcwd()
  for file in os.listdir(filepath):  
      name, ext = os.path.splitext(file)
      if ext.lower()==".stl":
        otherfiles.append(file)  
  otherfiles=sorted(otherfiles)
  # Quit if no STL files found
  if len(otherfiles)==0:
      print ("No STL files found to display.")
      quit()
  argsList=["file:"+otherfiles[0],]

# If we only have a filename as argument (without key 'file:') 
# which is format used by OS to open viewer for selected file in fileexplorer
if len(argsList)==1 and not ":" in argsList[0]:
  print (argsList)
  argsList=["file:"+argsList[0],]
  print (argsList)

# Otherwise we have a full command line, so we split arguments
args={}
for argItem in argsList:
  if not ":" in argItem:
    print ("Arguments must have key! \nE.g. 'file:myfile.stl'\nValid keys are 'file','auto','size'")
    quit()
  argKey=argItem.split(":")[0]
  argVal=argItem.split(":")[1]
  args[argKey]=argVal
  #print (argItem,argKey,argVal)  

# If file is missing we quit
if not 'file' in args:
  print ("Please specify file.")
  quit()

# If invalid filename we quit
filename=args['file']
if not os.path.isfile(filename):
  print ("File not found.")
  quit()

# Create list of other files so we can navigate
absfilename=os.path.abspath(filename)
filepath=os.path.split(filename)[0]
if filepath in ('','.'):
  filepath=os.getcwd()

otherfiles=[] 
for file in os.listdir(filepath):  
    name, ext = os.path.splitext(file)
    if ext.lower()==".stl":
      otherfiles.append(file)

otherfiles=sorted(otherfiles)

idx=otherfiles.index(os.path.split(filename)[1])
last_idx=len(otherfiles)-1

# Extract window size if specified
if 'size' in args:
  size=args['size'].split(',')
  if len(size)!=2:
    print ("'size' value should have format 'width,height', e.g. '320,240'.")
    quit()
  w,h=int(size[0]),int(size[1])
else:
  w,h=240,240

###################################################

print ("Load init file - idx:",idx,otherfiles[idx])
nfilename=os.path.join(filepath,otherfiles[idx])

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
    if key=='a':
      print ("Fit image")
      fitImage()
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

    reader = vtk.vtkSTLReader()
    reader.SetFileName(nfilename)
    
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

    ren.SetBackground(0,0,0)
    renWin.Render()

    loading=False

# Create a rendering window and renderer
renWin = vtk.vtkRenderWindow()
renWin.SetWindowName("STLViewer")
renWin.SetSize(w,h)
ren = vtk.vtkRenderer()
reader=None;

# Create a renderwindowinteractor
iren = vtk.vtkRenderWindowInteractor()
iren.AddObserver('KeyPressEvent', keypress_callback, 1.0)
iren.SetRenderWindow(renWin)


# Assign actor to the renderer
actor=None

if 'auto' in args:
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

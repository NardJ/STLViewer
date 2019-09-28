# STLViewer v0.1
Lightweight STLViewer for python3, using vtk, cv2, numpy

## Disclaimer
FileMerger is alpha. There probably are bugs, the output files have not yet been tested on a real photon! Use at your own risk!

 ---
  
## Installation
You can run FileMerger in Windows, OSX(not tested) and Linux. Your OS must be 64 bit. 
There is no binary release so you have to install Python3-64bit.

0) Download the source code in zip or tar.gz.

1) Install Python **3**-**64bit** from https://www.python.org/downloads/  
__or__ install Anaconda 3.6 https://www.anaconda.com/download/ 

2) Check if the python version is above 3 and 64 bit by typing in the command line 'python --version'

3) Install the numpy and opencv libraries
   * type 'python -m pip install -U vtk --user' !!! not tested, could be wrong
   * type 'python -m pip install -U numpy --user'
   * type 'python -m pip install -U opencv-python --user'
   
4) You have two options to run PhotonViewer:
   * from your file explorer find and run STLViewer.py 
   * from a dos prompt/linux terminal, navigate to the directory where you extracted the zip file and type 'python STLViewer.py' for windows or 'phyton3 STLViewer.py' for linux.

**Attention: STLViewer will not work with Python 2 or in a 32 bit version of Python!** 

---
  
  
## Manual
Usage: STLViewer.py file:'yourfile.stl' optionalkey:value
       Valid optional keys are 'auto':None,'size':width,height

Controls: [mouse-left]: rotate, [mouse-wheel/right]: zoom, 
          [up]: change up vector, [space]: save screenshot
          [a]: shrink to fit screen

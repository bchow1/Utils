#!/usr/bin/python
import os
import sys

def dirContents(dirName,depth):
  fNames = []
  dirNames = []
  depth += 1
  for p in os.listdir(dirName):
    fullName = os.path.join(dirName,p)
    #print 'fullName = ',fullName
    if os.path.isdir(fullName):
      dirNames.append(fullName)
    else:
      fNames.append(p)
  if len(fNames) > 0:
    fNames.sort()
  spacing = "" 
  for d in range(depth):
    spacing += "  " 
  for fName in fNames:
    print spacing,'|--',fName
  for dName in dirNames:
    print spacing,'%d--'%depth,dName.split(os.path.sep)[-1]+'/','[',dName,']'
    #print 'call dirContents for ',dName,depth
    dirContents(dName,depth) 
  return
    
if len(sys.argv) > 1:
  baseDir = sys.argv[1]
else:
  baseDir = "./"

depth = 0
dirContents(baseDir,depth)

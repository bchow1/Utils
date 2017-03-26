#!/bin/python

import os
import re
import sys
import fileinput
import subprocess

udfDict = {}
dfdDict = {}
defDict = {}
isDone  = []

def listDef(fName,spaces=''):

  spaces = spaces + '|-'
  if fName in isDone:
    return
  else:
    isDone.append(fName)

  try:
    udNames = udfDict[fName]
    print spaces,'**',fName 
  except KeyError:
    print spaces,fName," Not Available"
    return
    
  for udfName in udNames:
    try:
      dfFile = defDict[udfName]
      outString = udfName + " <- " + dfFile
      print spaces,outString
      listDef(dfFile,spaces=spaces)
    except KeyError:
      print spaces,udfName," Not Available"
  return

binDir = 'ifort'
startFile = 'OutputProcess'

udfPattern = re.compile(r'.*\s+U\s+(\w+)')
defPattern = re.compile(r'.*\s+T\s+(\w+)')

fList = []
for root,dirs,files in os.walk(binDir):
  for fName in files:
    if fName.lower().endswith('.o'):
      fList.append(os.path.join(root,fName))
      print 'fName = ',os.path.join(root,fName)

print os.listdir('./')
rmCmd = ["rm","-f","objList.tmp"]


for fName in fList:
  #print fName
  outFile = open("objList.tmp",'w')
  command = ['nm',"%s"%fName]
  #print 'Command = ',command
  errmsg = subprocess.Popen(command,stdout=outFile,
                                            stderr=subprocess.PIPE).communicate()
  #print errmsg
  outFile.close()
  udfList = []
  defList = []
  for line in fileinput.input('objList.tmp'):
    udf = udfPattern.match(line)
    if udf:
       fncName = udf.group(1)
       if fncName not in udfList:
         udfList.append(udf.group(1))
    dfd = defPattern.match(line)
    if dfd:
       fncName = dfd.group(1)
       if fncName not in defList:
         defList.append(dfd.group(1))
  udfDict.update({fName:udfList})
  dfdDict.update({fName:defList})
  os.remove('objList.tmp')
  if '%s.o'%startFile in fName:
    startFile = fName
  for defName in defList:
    if defName not in defDict.keys():
      defDict.update({defName:fName})
   
print startFile
listDef(startFile)
#for udfName in udfDict[startFile]:
  #try:
  #  outString = udfName + " <- " + defDict[udfName]
  #  print 
  #except KeyError:
  #  print udfName," Not Available"


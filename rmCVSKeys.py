import os
import sys
import shutil
import re
import fileinput
import difflib

# patterns
cvsKeyPatt  = re.compile('^!\$(.*?):(.*)\$$')
exts = ('.f','.f90','.F','.F90')

def getFnames(baseDir='.'):
  fList = []
  for root,dirs,files in os.walk(baseDir):
    for fName in files:
      if fName.endswith(exts):
        print os.path.join(root,fName)
        fList.append(os.path.join(root,fName))
  return fList

def rmCVSKey(string):
  newString = None
  match = cvsKeyPatt.match(string) 
  if match is not None:
    newString = '!$%s$\n'%match.group(1)
  return newString

if __name__ == '__main__':

  isFile = False
  if sys.argv.__len__() > 1:
    if 'FILE:' in sys.argv[1]:
      fNames = sys.argv[1].replace('FILE:','')
      isFile = True
      ans = 'y'
      #ans = raw_input('Remove CVS keyword values from files %s\n Continue? '%sys.argv[1])
    else:
      dName = sys.argv[1]
      ans = raw_input('  Remove CVS keyword values from files in %s\n Continue? '%dName)
  else:
    print 'Usage: rmCVSKeys.py (dirname|FILE:filename)'
    sys.exit()


  if ans == 'n' or ans == 'N':
    sys.exit()
  if not isFile:
    os.chdir(dName)
    print 'Current dir = ',os.getcwd()
  
  if isFile:
    fList = fNames.split(';')
  else:
    fList = getFnames()
    #print fList

  rename = False
  for fName in fList:
    print 'Examining file ',fName
    newHName = fName+'.new'
    fNew = open(newHName,'w')
    for line in fileinput.input(fName):
      if line.startswith('!$'):
        newLine = rmCVSKey(line) 
      else:
        newLine = None
      if newLine is None:
        fNew.write('%s'%line)
      else:
        rename = True
        fNew.write('%s'%newLine)
    fileinput.close()
    fNew.close()
    if rename:
      try:
        print 'Processed file: %s'%fName
        shutil.move(newHName,fName)
      except OSError:
        print 'Failed moving %s to %s in %s'%(newHName,fName,os.getcwd())

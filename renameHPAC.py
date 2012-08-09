import os
import sys
import re
import fileinput

# local modules
import utilDb

# patterns
hpacPatt  = re.compile('(.*)hpac(.*)',re.I)

def getFnames(baseDir='./'):
  fList = []
  for root,dirs,files in os.walk(baseDir):
    for fName in files:
      if fName.endswith('vfproj') or \
         fName.endswith('vcproj') or \
         fName.endswith('sln') or \
         fName.endswith('f90'):        
        fList.append(os.path.join(root,fName))
  return fList

def replaceH(string):
  newString = None
  if hpacPatt.match(string):
    newString = string
    if 'HPAC' in newString:
      newString = newString.replace('HPAC','SCIP')
    if 'hpac' in newString:
      newString = newString.replace('hpac','scip')
    if 'Hpac' in newString:
      newString = newString.replace('Hpac','Scip')
  return newString

if __name__ == '__main__':


  #os.chdir('D:\\hpac\\SCIPUFF\\export\\SCICHEM\\120719\\workspace\\EPRI')
  #os.chdir('D:\\hpac\\SCIPUFF\\export\\SCICHEM\\120719\\src\\sys\\windows')
  os.chdir('D:\\hpac\\SCIPUFF\\export\\SCICHEM\\120719')
  fList = getFnames()
  for fName in fList:
    print 'File ',fName
    newHName = fName+'.new'
    fNew = open(newHName,'w')
    for line in fileinput.input(fName):
      newLine = replaceH(line)
      if newLine is not None:
        fNew.write('%s'%newLine)
      else:
        fNew.write('%s'%line)
    fileinput.close()
    fNew.close()
    os.remove(fName)
    newSName = replaceH(fName)
    if newSName is not None:
      try:
        os.rename(newHName,newSName)
      except OSError:
        print 'Error: renaming ',newHName,' to ',newSName
        sys.exit()
    else:
      try:
        os.rename(newHName,fName)
      except OSError:
        print 'Error: renaming ',newHName,' to ',fName
        sys.exit()

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
      fList.append(os.path.join(root,fName))
  return fList

def replaceH(string):
  newString = None
  print string
  if hpacPatt.match(string):
    print 'Found match'
    newString = string
    if 'HPAC' in newString:
      newString = newString.replace('HPAC','SCIP')
    if 'hpac' in newString:
      newString = newString.replace('hpac','scip')
    if 'Hpac' in newString:
      newString = newString.replace('Hpac','Scip')
  return newString

if __name__ == '__main__':

  os.chdir('D:\\hpac\\gitEPRI\\src\\lib\\SCIPUFFlib\\SCIPUFF')
  fList = ['runHPAC.f90'] #getFnames()
  for fName in fList:
    print 'Working on file ',fName
    newHName = fName+'.new'
    fNew = open(newHName,'w')
    for line in fileinput.input(fName):
      newLine = replaceH(line)
      if newLine is not None:
        fNew.write('%s'%newLine)
        print 'newLine:',newLine
      else:
        fNew.write('%s'%line)
    fileinput.close()
    fNew.close()
    os.remove(fName)
    newSName = replaceH(fName)
    if newSName is not None:
      os.rename(newHName,newSName)
      print 'newSNname:',newSName
    else:
      os.rename(newHName,fName)
  

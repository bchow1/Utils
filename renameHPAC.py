import os
import sys
import shutil
import re
import fileinput

# patterns
hpacPatt  = re.compile('(.*)hpac(.*)',re.I)
exts = ('.f','.f90','.F','.F90','.mak','.sh','.vfproj','.vcproj','.sln')

def getFnames(baseDir='.'):
  fList = []
  dList = []
  excludes = [os.path.join(baseDir,'.git'),os.path.join(baseDir,'lib'),'workspace','CVS'] # for dirs and files
  for root,dirs,files in os.walk(baseDir,topdown=True):
    # exclude dirs
    dirs[:] = [d for d in dirs if os.path.join(root,d) not in excludes]
    dList.append(os.path.join(root,d))
    for fName in files:
      if fName.endswith(exts):
        print os.path.join(root,fName)
        fList.append(os.path.join(root,fName))
  return dList,fList

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

  errList = []
  #os.chdir('D:\\hpac\\SCIPUFF\\export\\SCICHEM\\120719\\workspace\\EPRI')
  #os.chdir('D:\\hpac\\SCIPUFF\\export\\SCICHEM\\120719\\src\\sys\\windows')
  os.chdir('D:\\SCIPUFF\\Repository\\EPA_Processed\\')
  ans = raw_input('Renaming directories and files in %s.\n Continue? '%os.getcwd())
  if ans == 'n' or ans == 'N':
    sys.exit()
  
  dList,fList = getFnames()
  for fName in fList:
    newHName = fName +'.new'
    fNew = open(newHName,'w')
    for line in fileinput.input(fName):
      newLine = replaceH(line)
      if newLine is not None:
        fNew.write('%s'%newLine)
      else:
        fNew.write('%s'%line)
    fileinput.close()
    fNew.close()
    print 'Rewriting %s as %s'%(fName,newHName)
    os.remove(fName)

    newSName = replaceH(fName)
    if newSName is not None:      
      try:
        dName = os.path.dirname(newSName)
        if not os.path.exists(dName):          
          print 'Creating dir ',dName
          os.makedirs(dName)
        shutil.move(newHName,newSName)
        print 'Renaming %s to %s in %s'%(newHName,newSName,os.getcwd())
      except OSError:
        print 'Failed renaming %s to %s in %s'%(newHName,newSName,os.getcwd())
        errList.append('mv -v %s %s'%(newHName.replace('\\',r'/'),newSName.replace('\\',r'/')))
        continue
    else:
      try:
        dName = os.path.dirname(fName)
        if not os.path.exists(dName):
          os.makedirs(dName)
          print 'Creating dir ',dName
        shutil.move(newHName,fName)
        print 'Moving %s to %s in %s'%(newHName,fName,os.getcwd())
      except OSError:
        print 'Failed moving %s to %s in %s'%(newHName,fName,os.getcwd())
        errList.append('mv -v %s %s'%(newHName.replace('\\','/'),fName.replace('\\','/')))
        continue
  if len(errList) > 0:
    reNameF = open('reName.sh','w')
    for line in errList:
      reNameF.write('%s\n'%line)
    reNameF.close()
 
  

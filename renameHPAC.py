import os
import sys
import shutil
import re
import fileinput

# patterns
hpacPatt  = re.compile('(.*)hpac(.*)',re.I)
exts = ('.f','.f90','.F','.F90','.mak','.sh','.vfproj','.vcproj','.sln')
#exts = ('.new')

def getFnames(baseDir='.'):
  fList = []
  for root,dirs,files in os.walk(baseDir):
    for fName in files:
      if fName.endswith(exts):
        print os.path.join(root,fName)
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

  isFile = False
  if sys.argv.__len__() > 1:
     arg1 = sys.argv[1]
     if 'FILE:' in arg1:
       arg1 = arg1.replace('FILE:','')
       isFile = True
       ans = raw_input('Rename files %s\n Continue? '%arg1)
     else:
       os.chdir(arg1)
       ans = raw_input('Renaming directories and files in %s.\n Continue? '%os.getcwd())
  else:
    #os.chdir('D:\\hpac\\SCIPUFF\\export\\SCICHEM\\120719\\workspace\\EPRI')
    #os.chdir('D:\\hpac\\SCIPUFF\\export\\SCICHEM\\120719\\src\\sys\\windows')
    #os.chdir('D:\\SCIPUFF\\Repository\\EPRI_STE\\')
    #os.chdir('D:\\hpac\\SCIPUFF\\export\\SCICHEM\\120719\\workspace\\EPRI')
    #os.chdir('D:\\hpac\\SCIPUFF\\export\\SCICHEM\\120719\\src\\sys\\windows')
    os.chdir('D:\\SCIPUFF\\EPRI_WIP\\Processed_Tmp\\src')
    ans = raw_input('Renaming directories and files in %s.\n Continue? '%os.getcwd())

  if ans == 'n' or ans == 'N':
    sys.exit()
  
  errList = []
  if isFile:
    fList = arg1.split(';')
  else:
    fList = getFnames()
  for fName in fList:
    print 'rename File:',fName
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

    '''
    # Use following lines to rename .new files. Must create SCIP directories manually
    newHName = fName[2:]
    print newHName
    newSName = replaceH(newHName.replace('.new',''))
    print newSName
    '''
    newSName = replaceH(fName)
    if newSName is not None:
      try:
        dName = os.path.dirname(newSName)
        if not os.path.exists(dName):          
          print 'Creating dir ',dName
          os.makedirs(dName)
        shutil.move(newHName,newSName)
        #print 'Renaming %s to %s in %s'%(newHName,newSName,os.getcwd())        
      except OSError:
        print 'Failed renaming %s to %s in %s'%(newHName,newSName,os.getcwd())
        errList.append('mv -v %s %s'%(newHName.replace('\\',r'/'),newSName.replace('\\',r'/')))
        continue        
        #print 'Error: renaming ',newHName,' to ',newSName
        #break
    else:
      try:
        dName = os.path.dirname(fName)
        if len(dName.strip()) > 1:
          print 'dName = "',dName,'"'
          if not os.path.exists(dName):
            os.makedirs(dName)
            print 'Creating dir ',dName
        shutil.move(newHName,fName)
        print 'Moving %s to %s in %s'%(newHName,fName,os.getcwd())        
      except OSError:
        #print 'Error: renaming ',newHName,' to ',fName
        #break
        print 'Failed moving %s to %s in %s'%(newHName,fName,os.getcwd())
        errList.append('mv -v %s %s'%(newHName.replace('\\','/'),fName.replace('\\','/')))
        continue
  if len(errList) > 0:
    reNameF = open('reName.sh','w')
    for line in errList:
      reNameF.write('%s\n'%line)
    reNameF.close()      

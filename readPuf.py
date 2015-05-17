#
import os
import sys
import socket
import subprocess
import fileinput
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from difflib import Differ
#
import run_cmd
import tab2db
import setSCIparams as SCI 

def createCSV(env,prjName,readpuf):

  pufFile = prjName + '.puf'
  if not os.path.exists(pufFile):
    print 'Error: cannot file puf file ',pufFile

  outFile = prjName + '.csv'
  if os.path.exists(outFile):
    os.remove(outFile)
    
  #
  Inputs = ('%s%s %s%s %s%s%s %s%s %s%s %s'% ('go ',pufFile,tail, 'time -1',tail, 'file CSV:',outFile,tail, \
                                                'go ',tail, 'exit', tail))
  print Inputs  
  run_cmd.Command(env,readpuf,Inputs,tail)
  #else: 
    #Inputs = (' %s%s %s%s %s%s%s %s%s'% ('RP',tail,'file TXT:'+ outFile,tail, 'go ',prjName,tail, 'exit', tail))
    #run_cmd.Command(env,readpuf,Inputs,tail)

def diffCSV(file1,file2,outFName):
  '''
  with open(file1) as f1, open(file2) as f2:
    differ = Differ()
    for line in differ.compare(f1.readlines(),f2.readlines()):
      if line.startswith(" "):
        print 'Same:',line[2:]
      else:
       print  'Diff:',line
       sys.exit()
  '''
  varNames = None
  tOld    = None
  nDiff   = 0
  with open(file1) as f1, open(file2) as f2, open(outFName,'w') as outFile:
    for line1,line2 in zip(f1,f2):
      if line1.startswith('"IPUF"'):
        print line1
        varNames = line1.replace('"','').split(',')
        print varNames
        #sys.exit()
      if varNames is None:
        continue
      if line1 == line2:
        colVals1 = line1.split(',')
        tVal = colVals1[1]
        if tVal != tOld:
          print 'Time = ',tVal
          tOld = tVal
      else:
        nDiff += 1
        colVals1 = line1.split(',')
        colVals2 = line2.split(',')
        outFile.write('Diff at times = %s and %s for npuff %s and %s\n'%(colVals1[1],colVals2[1],colVals1[0],colVals2[0]))        
        for colNo,colVar in enumerate(varNames):
          if colVals1[colNo] != colVals2[colNo]:
            outFile.write('%s, %s, %s\n'%(colVar,colVals1[colNo],colVals2[colNo]))
        outFile.write('\n')
        if nDiff > 10:
          break
  
  f1.close()
  f2.close()
  outFile.close()
  
  return
    
def csv2Db(prjName):
  csvFile = prjName + '.csv'
  dbFile  = prjName + '_puff.db'
  if os.path.exists(dbFile):
    os.remove(dbFile)
  dbConn = sqlite3.connect(dbFile)
  dbCur  = dbConn.cursor()
  # Drop tables
  dbCur.execute('DROP table if exists puffTable')
  dbCur.execute('DROP table if exists massTable')
  dbCur.execute('DROP table if exists concTable')
  dbCur.execute('DROP table if exists ambTable')
  # Get puff var names and species names
  for line in fileinput.input(csvFile):
    if env["SCICHEM"] == "True":
      headNo = 1
    else:
      headNo = 3
    if fileinput.lineno() == headNo:
      varNames = line.strip().replace('#','').replace('"','').split(',')
      if len(varNames[-1])< 1:
        varNames = varNames[:-1]
      break
  fileinput.close()

  # Get colNos for varNames
  puffList = []
  colNos   = {}
  spNames  = []
  for vNo,vName in enumerate(varNames):
    vName = vName.strip().replace('-','_')
    colNos.update({vName:vNo})
    vPrefix = vName[:2]
    if vPrefix == 'C_' or \
       vPrefix == 'A_' or \
       vPrefix == 'S_':
      continue
    elif vPrefix == 'M_':
      spNames.append(vName[2:])
    else:
      puffList.append(vName)
  #print varNames
  #keys = colNos.keys()
  #keys.sort()
  #for key in keys:
  #  print colNos[key],key
  #print '\npuffList = ',puffList
  #print '\nspNames = ',spNames
  massList = concList = ambList = ctotList = spNames 
  
  tableNames = ['puffTable', 'massTable', 'concTable', 'ambTable', 'ctotTable']
  nameLists  = [puffList, massList, concList, ambList, ctotList]


  # Create tables
  for tNo,tName in enumerate(tableNames):
    createStr = 'CREATE table %s ('%tName
    createStr += 'puffId int, '
    if tName != 'puffTable':
      createStr += 'species varchar(20), value real)'
    else:      
      for i in range(len(nameLists[tNo])):
        createStr += nameLists[tNo][i] + ' real, '  
      createStr = createStr[:-2] + ')'
    print '\n',createStr
    dbCur.execute(createStr)
  dbConn.commit()
  # Insert data for tables
  nPVar = len(puffList)
  for line in fileinput.input(csvFile):
    if fileinput.lineno() <= headNo:
      continue
    colValues = line.strip().split(',')
    puffId = fileinput.lineno() - headNo
    print 'puffId = ',puffId,' at time ',colValues[1]
    for tNo,tName in enumerate(tableNames):
      if tName == 'puffTable':
        insertStr = 'INSERT into %s VALUES('%tName
        insertStr += '%d ,'%puffId
      for i in range(len(nameLists[tNo])):
        if tName != 'puffTable':
          insertStr = 'INSERT into %s VALUES('%tName
          insertStr += "%d , '%s' ,"%(puffId,nameLists[tNo][i])
        colHead = nameLists[tNo][i]
        if tName == 'ctotTable':
          val = 0.
          for pre in ['C_','A_']:
            preHead = pre + colHead
            try:
              j    = colNos[preHead]
              val += float(colValues[j])
            except KeyError:
              val = -9999.
              break
          val = '%15.5e'%val
        else:
          if tName == 'massTable':
            colHead = 'M_' + colHead
          if tName == 'concTable':
            colHead = 'C_' + colHead
          if tName == 'ambTable':
            colHead = 'A_' + colHead        
          try:
            j   = colNos[colHead]
            val = colValues[j].strip()
          except KeyError:
            val = '-9999.'
        if tName == 'puffTable':
          insertStr += val + ', '
        else:
          insertStr += val + ')'
          dbCur.execute(insertStr)
      if tName == 'puffTable':
        insertStr = insertStr[:-2] + ')'
        dbCur.execute(insertStr)
    dbConn.commit()
  fileinput.close()

  dbConn.commit()
  dbCur.close()
  dbConn.close()

def getHrDat(readpuf,env,prjName,hr,rmOut=False,tail='\n'):
  
  pufFile = prjName + '.puf'
  if not os.path.exists(pufFile):
    print 'Error: cannot file puf file ',pufFile

  if int(hr) == -1:
    outFile = prjName + '_All_puff.txt'
  else:    
    outFile = prjName + '_%08.2f_puff.txt'%hr
    
  if os.path.exists(outFile):
    if rmOut:
      os.remove(outFile)
      rmOut = True
  else:
    rmOut = True
    
  #
  if rmOut:
    if int(hr) == -1:
      Inputs = ('%s%s %s%s %s%s%s %s%s %s%s %s'%('go ',pufFile,tail,'time %8.2f'%hr,\
                 tail, 'file TXT:',outFile,tail,'go ',tail, 'exit', tail))
    else:
      Inputs = ('go %s \ntime -1 \nvar C \nfile TXT:%s \ngo \nexit\n'%(pufFile,outFile))      
    print Inputs
    run_cmd.Command(env,readpuf,Inputs,tail,outOut=True)
  
  vNames = {}
  if os.path.exists(outFile):
    hrDat = np.loadtxt(outFile,skiprows=3)
    oFile = open(outFile)
    lNo = 0
    for line in oFile:
      if lNo == 0:
        nVar = int(line.strip())
      if lNo == 1:
        varNames = line.strip().split()
        break
      lNo += 1
    oFile.close()

    for vNo,vName in enumerate(varNames):
      vNames.update({vName:vNo})
    #print vNames

    #zLt200 = hrDat[hrDat[:,vNames['Z']]< 200.]
    #C = zLt200[:,vNames['C']]
    #print len(C),np.sum(C)

    #zGt200 = hrDat[hrDat[:,vNames['Z']]> 200.]
    #C = zGt200[:,vNames['C']]
    #print len(C),np.sum(C)

  else:
    print 'Error: Cannot find %s'%outFile
    hrDat = np.array([-9999.])
  
  return vNames,hrDat

def pltHrDat(hrDat,hrLbl,vNames,vPltNms,vLims=None,vType=['lin','log'],ihr=0):
    #
  xIndx = vNames[vPltNms[0]]
  yIndx = vNames[vPltNms[1]]
  
  ax = fig.add_subplot(1,1,1)
  ax.plot(hrDat[:,xIndx],hrDat[:,yIndx],marker='o',markersize=3,linestyle='None',color=clrs[ihr])
  if vType[0] == 'log':
    ax.set_xscale('log')
  if vType[1] == 'log':
    ax.set_yscale('log')
    
  return

def plotHr2d(): 
   
  vPltNms  = [['C','ZI']] # ,['X','C'],['Y','C']]
  vLims    = [[None,-100],[None,[0.,2500.]],None,None]
  vTypes   = [['log','lin'],['lin','log'],['lin','log']]
  
  hrs = [i for i in range(39,41)]
  mark = ['+','s','d']
  clrs = ['red','blue','green']
  
  for prjName in prjNames.split(':'):
    
    for pltNo in range(len(vPltNms)):
      
      fig = plt.figure()
      plt.clf()
      plt.hold(True)
      
      for ihr,hr in enumerate(hrs):
        vNames,hrDat = getHrDat(readpuf,env,prjName,hr,tail=tail)
        print hr,len(hrDat[:,vNames['C']]),np.sum(hrDat[:,vNames['C']])
        hrLbl = '%02d'%hr
        
        # Check if variable in vNames list
        if vPltNms[pltNo][0] not in vNames or vPltNms[pltNo][1] not in vNames:
          print 'Cannot find ',vPltNms[pltNo][0],' or ',vPltNms[pltNo][1]
          print 'Valid variable names are :\n****'
          vList = vNames.keys()
          vList.sort()
          for iKey,Key in enumerate(vList):
            sys.stdout.write('%s'%Key)
            if (iKey+1)%20 == 0:
              tail = '\n'
            else:
              tail = ', '
            sys.stdout.write('%s'%tail)
          sys.stdout.write('\n****\n')
          sys.exit()
                            
        pltHrDat(hrDat,hrLbl,vNames,vPltNms[pltNo],vLims=vLims[pltNo],vType=vTypes[pltNo],ihr=ihr)
      
      plt.xlabel(vPltNms[pltNo][0])
      plt.ylabel(vPltNms[pltNo][1])
  
      if vLims[pltNo] is not None:
        if vLims[pltNo][0] is not None:
          plt.xlim(vLims[pltNo][0])
        if vLims[pltNo][1] is not None:
          plt.ylim(vLims[pltNo][1])
          
      title = 'Hr%s_%s_vs_%s'%(hrLbl,vPltNms[pltNo][0],vPltNms[pltNo][1])
      plt.title(title)
      
      plt.hold(False)
      #plt.show()
      figName = 'Hr%s_%s_vs_%s.png'%(hrLbl,vPltNms[pltNo][0],vPltNms[pltNo][1])
      plt.savefig(figName)
      print 'Created %s in %s'%(figName,os.getcwd())
  
  return

  
if __name__ == '__main__':

  #runDir = './'

  #runDir = '/home/user/bnc/scipuff/EPRI_121001/runs/aermod/martin/case4'
  #sys.argv = ['','mc_ter']

  #runDir = 'D:\\Aermod\\v12345\\runs\\martin\\SCICHEM'
  #runDir = 'D:\\SCIPUFF\\runs\\EPRI\\Ana\\trac'
  #runDir = '/home/user/bnc/scipuff/Repository/export/EPRI/EPRI_130620/test'
  runDir = '/home/user/bnc/scipuff/runs/AFTAC/OpenMP'
  
  # prjName as 2nd argument
  #sys.argv = ['','trac_jan']
  sys.argv = ['','stLouis2/stLouis_p1:stLouis_SS3_2008/scipuff'] # 
  

  if len(sys.argv) > 1:
    prjNames = sys.argv[1]
  else:
    print 'Usage: readPuf.py prjName1[:prjName2 ...]'
    sys.exit()

  compName = socket.gethostname()

  env = os.environ.copy()
  env["SCICHEM"] = "False"
  if sys.platform == 'win32':
    compiler = "intel"
    version = "Debug"
    if env["SCICHEM"] == "True":
      if compName == 'sm-bnc' or compName == 'sage-d600':
        SCIPUFF_BASEDIR="D:\\SCIPUFF\\EPRI_WIP"
        binDir = os.path.join(SCIPUFF_BASEDIR,"workspace","EPRI","vs2008","bin",compiler,"Win32",version)
        iniFile = "D:\\SCIPUFF\\Repository\\workspace\\EPRI\\scipuff.ini"
      env["PATH"] = "%s" % (binDir)
      readpuf  = ["%s\\scipp.exe"%binDir,"-I:%s"%iniFile,"-R:RP"]
    else:
      if compName == 'sm-bnc' or compName == 'sage-d600':
        SCIPUFF_BASEDIR="D:\\SCIPUFF\\EPRIx\\SCICHEM-2012\\"
        binDir = os.path.join(SCIPUFF_BASEDIR,"workspace","EPRI","bin",compiler,"Win32",version)
        iniFile = "D:\\SCIPUFF\\EPRIx\\SCICHEM-2012\\workspace\\EPRI\\scipuff.ini"
      env["PATH"] = "%s" % (binDir)
      print env["PATH"]
      readpuf  = ["%s\\scipp.exe"%binDir,"-I:%s"%iniFile,"-R:RP"]
    tail = '\r\n'
  else:
    SCIPUFF_BASEDIR = "/home/user/bnc/scipuff/Repository/UNIX/AFTACx64/bin/linux/ifort"
    #SCIPUFF_BASEDIR = "/home/user/bnc/scipuff/EPRI_121001/UNIX/EPRI/bin/linux/lahey_debug"
    #SCIPUFF_BASEDIR = "/usr/pc/biswanath/hpac/gitEPRI/UNIX/EPRI/bin/linux/lahey"
    readpuf = ["%s/scipp" % SCIPUFF_BASEDIR,"-I:scipuff.ini","-R:RP"]
    #env["LD_LIBRARY_PATH"] = "/usr/local/lf9562/lib:/home/user/bnc/gfortran/x86_32:/home/user/bnc/sqlite3/flibs-0.9/lib/gfort:/home/user/sid/HDF"
    #env["LD_LIBRARY_PATH"] = env["LD_LIBRARY_PATH"] + ':' + SCIPUFF_BASEDIR
    tail = '\n'

  #myEnv = SCI.setEnv(SCIPUFF_BASEDIR=SCIPUFF_BASEDIR)
  print readpuf

  # Set run directory
  os.chdir(runDir)
  print os.getcwd()
  
  #plotHr2d()

  prjNames = prjNames.split(':')
  for prjName in prjNames:
    #createCSV(env,prjName,readpuf)
    #csv2Db(prjName)
    if prjName != prjNames[0]:
      print prjNames[0]+'.csv',prjName+'.csv'
      diffCSV(prjNames[0]+'.csv',prjName+'.csv','puffDiffs.txt')
      
  


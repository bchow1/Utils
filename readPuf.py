#
import os
import sys
import socket
import subprocess
import fileinput
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
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

  outFile = prjName + '_%08.2f_puff.txt'%hr
  if os.path.exists(outFile):
    if rmOut:
      os.remove(outFile)
  else:
    rmOut = True
    
  #
  if rmOut:
    Inputs = ('%s%s %s%s %s%s%s %s%s %s%s %s'%('go ',pufFile,tail,'time %8.2f'%hr,\
              tail, 'file TXT:',outFile,tail,'go ',tail, 'exit', tail))
    print Inputs
    run_cmd.Command(env,readpuf,Inputs,tail)
  
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
    print vNames

    zLt200 = hrDat[hrDat[:,vNames['Z']]< 200.]
    C = zLt200[:,vNames['C']]
    print len(C),np.sum(C)

    zGt200 = hrDat[hrDat[:,vNames['Z']]> 200.]
    C = zGt200[:,vNames['C']]
    print len(C),np.sum(C)

  else:
    print 'Error: Cannot find %s'%outFile
    hrDat = np.array([-9999.])
  
  return vNames,hrDat

def pltHrDat(hrDat,hrLbl,vNames,vPltNms):
  fig = plt.figure()
  plt.clf()
  plt.hold(True)
  mark = ['+','s','d']
  clrs = ['red','blue','green']
  #
  vPltNms = ['C','Z']
  xIndx = vNames[vPltNms[0]]
  yIndx = vNames[vPltNms[1]]
  ax = fig.add_subplot(2,2,1)
  ax.semilogx(hrDat[:,xIndx],hrDat[:,yIndx],marker='o',markersize=3,linestyle='None',color='red')
  plt.xlabel(vPltNms[0])
  plt.ylabel(vPltNms[1])
  plt.ylim([0,200])
  title = 'Hr%s_%s_vs_%s'%(hrLbl,vPltNms[0],vPltNms[1])
  plt.title(title)
  plt.hold(False)
  plt.show()
  #plt.savefig('Hr%s_%s_%s_vs_%s.png'%(hrLbls[0],hrLbls[1],vPltNms[0],vPltNms[1]))
  
  return
  
if __name__ == '__main__':

  #runDir = './'

  #runDir = '/home/user/bnc/scipuff/EPRI_121001/runs/aermod/martin/case4'
  #sys.argv = ['','mc_ter']

  #runDir = 'D:\\Aermod\\v12345\\runs\\martin\\SCICHEM'
  runDir = '/home/user/bnc/scipuff/Repository/export/EPRI/EPRI_130620/test'
  sys.argv = ['','lin']

  if len(sys.argv) > 1:
    prjNames = sys.argv[1]
  else:
    print 'Usage: readPuf.py prjName1[:prjName2 ...]'
    sys.exit()

  compName = socket.gethostname()

  env = os.environ.copy()
  env["SCICHEM"] = "True"
  if sys.platform == 'win32':
    compiler = "intel"
    version = "Debug"
    if env["SCICHEM"] == "True":
      if compName == 'sm-bnc' or compName == 'sage-d600':
        SCIPUFF_BASEDIR="D:\\SCIPUFF\\EPRIx\\SCICHEM-2012\\"
        binDir = os.path.join(SCIPUFF_BASEDIR,"workspace","EPRI","bin",compiler,"Win32",version)
        iniFile = "D:\\SCIPUFF\\EPRIx\\SCICHEM-2012\\workspace\\EPRI\\scipuff.ini"
      env["PATH"] = "%s" % (binDir)
      readpuf  = ["%s\\scipp.exe"%binDir,"-I:%s"%iniFile,"-R:RP"]
    else:
      if compName == 'sm-bnc' or compName == 'sage-d600':
        SCIPUFF_BASEDIR="D:\\SCIPUFF\\EPRIx\\SCICHEM-2012\\"
        binDir = os.path.join(SCIPUFF_BASEDIR,"workspace","EPRI","bin",compiler,"Win32",version)
        iniFile = "D:\\SCIPUFF\\EPRIx\\SCICHEM-2012\\workspace\\EPRI\\scipuff.ini"
      env["PATH"] = "%s" % (binDir)
      readpuf  = ["%s\\scipp.exe"%binDir,"-I:%s"%iniFile,"-R:RP"]
      #OldPath = env["PATH"]
      #bindir = SCIPUFF_BASEDIR + "\\" + compiler + "\\" + version
      #urbdir = SCIPUFF_BASEDIR + "\\" + compiler + "\\nonurban"  + "\\" + version
      #vendir = SCIPUFF_BASEDIR + "\\vendor" 
      #env["PATH"] = "%s;%s;%s;%s" % (bindir,urbdir,vendir,OldPath)
      #env["PATH"] = "%s;%s;%s" % (bindir,urbdir,vendir)
      print env["PATH"]
      readpuf  = ["%s\\scipp.exe"%binDir,"-I:%s"%iniFile,"-R:RP"]
    tail = '\r\n'
  else:
    SCIPUFF_BASEDIR = "/home/user/bnc/scipuff/Repository/UNIX/EPRI/bin/linux/ifort"
    #SCIPUFF_BASEDIR = "/home/user/bnc/scipuff/EPRI_121001/UNIX/EPRI/bin/linux/lahey_debug"
    #SCIPUFF_BASEDIR = "/usr/pc/biswanath/hpac/gitEPRI/UNIX/EPRI/bin/linux/lahey"
    readpuf = ["%s/scipp" % SCIPUFF_BASEDIR,"-I:","-R:RP"]
    env["LD_LIBRARY_PATH"] = "/usr/local/lf9562/lib:/home/user/bnc/gfortran/x86_32:/home/user/bnc/sqlite3/flibs-0.9/lib/gfort:/home/user/sid/HDF"
    env["LD_LIBRARY_PATH"] = env["LD_LIBRARY_PATH"] + ':' + SCIPUFF_BASEDIR
    tail = '\n'

  #myEnv = SCI.setEnv(SCIPUFF_BASEDIR=SCIPUFF_BASEDIR)
  print readpuf

  # Set 
  os.chdir(runDir)
  
  #
  vPltNms = ['C','Z']
  hrs = [i for i in range(12,21)]
  for prjName in prjNames.split(':'):
    for ihr,hr in enumerate(hrs):
      vNames,hrDat = getHrDat(readpuf,env,prjName,hr,tail=tail)
      hrLbl = 'Hr %02d'%hr
      pltHrDat(hrDat,hrLbl,vNames,vPltNms)
  #
  '''
  for prjName in prjNames.split(':'):
    createCSV(env,prjName,readpuf)
    csv2Db(prjName)
  '''


#
import os
import sys
import ast
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
    
  if env["SCICHEM"] == "True":
    Inputs = ('%s%s %s%s %s%s%s %s%s %s%s %s'% ('go ',pufFile,tail, 'time -1',tail, 'file CSV:',outFile,tail, \
                                                'go ',tail, 'exit', tail))
    print Inputs  
    run_cmd.Command(env,readpuf,Inputs,tail)
  else: 
    Inputs = (' %s%s %s%s %s%s%s %s%s'% ('RP',tail,'file TXT:'+ outFile,tail, 'go ',prjName,tail, 'exit', tail))
    run_cmd.Command(env,scipp,Inputs,tail)

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
    varNames = line.strip().replace('#','').split(',')
    break
  fileinput.close()

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
    createStr += 'puffNo int, '
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
    if fileinput.isfirstline():
      continue
    colValues = line.strip().split(',')
    puffId = fileinput.lineno()-1
    print 'puffNo = ',puffId,' at time ',colValues[1]
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
            val = colValues[j]
          except KeyError:
            val = '-9999.'
        #print colHead,j,val
        if tName == 'puffTable':
          insertStr += val + ', '
        else:
          insertStr += val + ')'
          #print insertStr
          dbCur.execute(insertStr)
      if tName == 'puffTable':
        insertStr = insertStr[:-2] + ')'
        #print insertStr
        dbCur.execute(insertStr)
    dbConn.commit()
  fileinput.close()

  dbConn.commit()
  dbCur.close()
  dbConn.close()
  
if __name__ == '__main__':

  env = os.environ.copy()
  env["SCICHEM"] = "True"
  if sys.platform == 'win32':
    if env["SCICHEM"] == "True":
      SCIPUFF_BASEDIR="D:\\EPRI\\git\\workspace\\Debug"
      runDir = "D:\EPRI\\git\\runs\\tva"
      readpuf = ["%s\\readpuf.exe" % SCIPUFF_BASEDIR]
    else:
      SCIPUFF_BASEDIR="D:\\hpac\\SCIPUFF\\bin"
      compiler = 'intel'
      version = 'debug'
      OldPath = env["PATH"]
      bindir = SCIPUFF_BASEDIR + "\\" + compiler + "\\" + version
      urbdir = SCIPUFF_BASEDIR + "\\" + compiler + "\\nonurban"  + "\\" + version
      vendir = SCIPUFF_BASEDIR + "\\vendor" 
      #env["PATH"] = "%s;%s;%s;%s" % (bindir,urbdir,vendir,OldPath)
      env["PATH"] = "%s;%s;%s" % (bindir,urbdir,vendir)
      print env["PATH"]
      readpuf  = ["%s\\scipp.exe" % bindir,"-I:","-R:RP"]
    tail = '\r\n'
  else:
    SCIPUFF_BASEDIR = "/home/user/bnc/hpac/fromSCIPUFF/Repository/UNIX/FULL/bin/linux/lahey"
    scipp = ["%s/postprocess" % SCIPUFF_BASEDIR,"-I:"]
    env["LD_LIBRARY_PATH"] = "/usr/local/lf9562/lib:/home/user/bnc/gfortran/x86_32:/home/user/bnc/sqlite3/flibs-0.9/lib/gfort:/home/user/sid/HDF"
    env["LD_LIBRARY_PATH"] = env["LD_LIBRARY_PATH"] + ':' + SCIPUFF_BASEDIR
    tail = '\n'

  #myEnv = SCI.setEnv(SCIPUFF_BASEDIR=SCIPUFF_BASEDIR)
  print readpuf

  # Set 
  prjName = 'noambstp'
  os.chdir(runDir)
  #
  #createCSV(env,prjName,readpuf)
  #
  csv2Db(prjName)
  #select time,ipuf,value from pufftable p, masstable m where p.puffno==m.puffno and m.species='NO2';

'''
fig = plt.figure()
fig.hold()
plt.scatter(sigDat[:,1],sigDat[:,2],c=sigDat[:,0])

xmin = min(sigDat[:,1].min(),sigDat[:,2].min())
xmax = max(sigDat[:,1].max(),sigDat[:,2].max())
yp5 = np.array(([0.,0.],[xmax,xmax/2.]))
y1 = np.array(([0.,0.],[xmax,xmax]))
y2 = np.array(([0.,0.],[xmax,2.*xmax]))

plt.plot(yp5[:,0],yp5[:,1])
plt.plot(y1[:,0],y1[:,1])
plt.plot(y2[:,0],y2[:,1])
plt.xlabel('Sigmax')
plt.ylabel('Si2')
plt.xlim([0.,xmax])
plt.ylim([0.,xmax])
plt.colorbar(fraction=0.08)
plt.savefig('temp.png')
os.remove(outFile) 
#print sigDat
'''

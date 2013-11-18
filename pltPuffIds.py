import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def iter_loadtxt(filename, delimiter=',', skiprows=0, dtype=float):
  def iter_func():
    with open(filename, 'r') as infile:
      for _ in range(skiprows):
        next(infile)
      for line in infile:
        line = line.rstrip().split(delimiter)
        for item in line:
          yield dtype(item)
    iter_loadtxt.rowlength = len(line)
  
  data = np.fromiter(iter_func(), dtype=dtype)
  data = data.reshape((-1, iter_loadtxt.rowlength))
  return data

def openFout(tEnd,tStep):
  
  fNo   = int(tEnd/tStep)
  fName = csvName.split('.')[0]+'_%d.csv'%fNo
  print 'Creating %s'%fName
  fOut = open(fName,'w')
  fOut.write('%s\n'%hdr)
  lOpen = False
  
  return (fOut,fName,lOpen)

def plotCsv(fName,tStart,tEnd,colName,colDtype):
  df = pd.read_csv(fName, sep=',', skiprows=1, names=colNames, dtype=colDtype)
  #print df.columns
  maxMass = df['mass'].max()
  print maxMass
  df['massR'] = map(int,(df['mass']/maxMass)*50)
  
  dfNew = df[(df.Parent1==0) & (df.Routine !='ZS0')]
  
  dfzs0 = df[(df.Routine =='ZS0')]
  #print dfzs0
  
  dfzs1 = df[(df.Routine =='ZS1')]
  print dfzs1
  
  dfzs2 = df[(df.Routine =='ZS2')]
  print dfzs2
  
  plt.clf()
  plt.hold(True)
  
  cA = ['red','green','blue','purple']
  mA = ['o','s','>','<']
  
  for ityp,dtyp in enumerate([dfNew,dfzs0,dfzs1,dfzs2]):
    plt.scatter(dtyp['Time'],dtyp['zbar'],color='white',alpha=0.5,edgecolors=cA[ityp],\
                marker=mA[ityp],s=dtyp['massR'])
  
  plt.title('Puffs for Time between %8.3f and %8.3f'%(tStart/3600.,tEnd/3600.))
  plt.xlabel('Time(Sec)')
  plt.ylabel('Zbar(m)')
  
  plt.hold(False)
  plt.show()
  
  return  

if sys.platform == 'win32':
  os.chdir('d:\\SCIPUFF\\runs\\AFTAC\\newMexico')
else:
  os.chdir('/home/user/bnc/scipuff/runs/AFTAC/newMexico_puffIds')
  
#pData = iter_loadtxt('puffTree_3hr.csv',skiprows=1)

csvName = 'puffTree_3hr.csv'
#csvName = 'pfTree3hr_1000.csv'

csvFile = open(csvName,'r')
lno = 0
tStart = 0.
tStep  = 900.
tEnd   = tStart + tStep
lOpen  = True
for line in csvFile:
  lno += 1
  line = line.strip().replace(' ','') # strip(' \t\n\r')
  if lno == 1:
    line = line.replace('#','')
    colNames = line.split(',')
    colTypes = []
    colDtype = {}
    for colNo,colNm in enumerate(colNames):
      colNm = colNm.strip()
      colNames[colNo] = colNm  
      if colNm in ['Routine']:
        colTypes.append('S4')
        colDtype.update({colNm:'|S4'})
      elif colNm in ['Parent1','Parent2','Self','Child1','Child2','TimeLevel']:
        colTypes.append('int')
        colDtype.update({colNm:np.int})
      else:
        colTypes.append('float')
        colDtype.update({colNm:np.float})
    hdr = line
    print hdr
    print colNames
    #print colTypes
    print colDtype
  else:
    colVals = line.split(',')
    time = float(colVals[0])
    if time > 3600.:
      break
    if time >= tStart and lOpen:
      fOut,fName,lOpen  = openFout(tEnd,tStep)
    if not lOpen and time > tEnd:
      fOut.close()
      plotCsv(fName,tStart,tEnd,colNames,colDtype)
      tStart           = tEnd
      tEnd             = tStart + tStep
      fOut,fName,lOpen = openFout(tEnd,tStep)
    fOut.write('%s\n'%line)

fOut.close()    
csvFile.close()

sys.exit()

#tp = pd.read_csv(csvName, iterator=True, sep=',', skiprows=1, names=colNames, dtype=colDtype, chunksize=1000)
#df = pd.concat(tp, ignore_index=True)
#print df



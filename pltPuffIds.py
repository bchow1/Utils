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

os.chdir('d:\\SCIPUFF\\runs\\AFTAC\\newMexico')
'''
#pData = iter_loadtxt('puffTree_3hr.csv',skiprows=1)
#tab2db.makeDb('puffTree_3hr.csv',separator=',',hdrlno=1)
#dbFile = fName + '.db'
print '\nCheck:'
print str(utilDb.db2List(dbFile,'select sql from sqlite_master where type="table"')[0][0])
dtype={'names':('Indx','L','Hflx'),'formats':('int','float','float')
'''
csvName = 'pfTree3hr_1000.csv'
#csvName = 'float.csv'

csvFile = open(csvName,'r')
lno = 0
for line in csvFile:
  lno += 1
  if lno == 1:
    colNames = line.strip(' \t\n\r').replace('#','').split(',')
    
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
  if lno > 2:
    break
csvFile.close()
print colNames
#print colTypes
#print colDtype


#dtype=[('A', 'i4'),('B', 'f4'),('C', 'a10')]
#tp = pd.read_csv(csvName, iterator=True, sep=',', skiprows=1, names=colNames, dtype=colDtype, chunksize=1000)
#df = pd.concat(tp, ignore_index=True)
#print df

df = pd.read_csv(csvName, sep=',', skiprows=1, names=colNames, dtype=colDtype)
#print df.columns
maxMass = df['mass'].max()
print maxMass
df['massR'] = map(int,(df['mass']/maxMass)*300)

dfNew = df[(df.Parent1==0) & (df.Routine !=' ZS0')]

dfzs0 = df[(df.Routine ==' ZS0')]
#print dfzs0

dfzs1 = df[(df.Routine ==' ZS1')]
print dfzs1

dfzs2 = df[(df.Routine ==' ZS2')]
print dfzs2

plt.clf()
plt.hold(True)

cA = ['red','green','blue','purple']
mA = ['o','s','>','<']

for ityp,dtyp in enumerate([dfNew,dfzs0,dfzs1,dfzs2]):
	plt.scatter(dtyp['Time'],dtyp['zbar'],color='white',alpha=0.5,edgecolors=cA[ityp],\
						  marker=mA[ityp],s=dtyp['massR'])
	
'''
plt.scatter(dfNew['Time'],dfNew['zbar'],color='white',alpha=0.5,edgecolors='red',marker='o',s=dfNew['massR'])
plt.scatter(dfzs0['Time'],dfzs0['zbar'],color='white',alpha=0.5,edgecolors='green',marker='s')
plt.scatter(dfzs1['Time'],dfzs1['zbar'],color='white',alpha=0.5,edgecolors='blue',marker='>')
plt.scatter(dfzs2['Time'],dfzs2['zbar'],color='white',alpha=0.5,edgecolors='purple',marker='<')
'''

plt.hold(False)
plt.show()

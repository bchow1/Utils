
#!/bin/env python
import os
import sys
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import sqlite3

# Local modules
sys.path.append('C:\\cygwin\\home\\sid\\python')
import utilDb

# Code for SCICHEM 2012 plots

def mainProg():
  os.chdir('D:\\SCICHEM-2012\\workspace')
  dataFile = '2009-10.SFC'
  #    9,   9,      1,    244    1         -40.9  0.755     -9.000   -9.000     -999.   1510.    927.9    0.1500   6.00   1.00       7.57    173.0    7.9     287.1    2.0     0     0.80    66.     987.    10      ADJ-A1
  
     
  #'S16','S8'
  LatLonArray = np.loadtxt(dataFile,skiprows=1,dtype={'names':('year','month','day','j_day','hour',    \
                                                               'H',   'u',      'w',     'VPTG' ,  'Zic',   \
                                                               'Zim',  'L',     'Zo'    , 'Bo',  'r',    \
                                                               'Ws',    'Wd',  'zref',   'temp', 'ztemp',\
                                                               'c1'  , 'c2'  ,'c3',   'c4'  , 'c5',    'c6'),\
                                                     'formats':('float','float','float','float','float'\
                                                                ,'float', 'float', 'float', 'float',  'float',\
                                                                'float', 'float', 'float', 'float', 'float'\
                                                                , 'float','float', 'float', 'float', 'float'\
                                                                 ,'float','float','float','float','float', 'S20'  )})
  print LatLonArray.shape
  
  for j in range (0, len(LatLonArray[0])):
    print j
    figName = 'Col%d.png'%j
    tcol = []
    xVal = []
    #for i in range(0,100):
    for i in range(0,len(LatLonArray)):
       tcur = LatLonArray[i]
       tcol.append(tcur[j])
       xVal.append(i)
       #ax.plot(tcol, 'o', markerfacecolor='None')
    #print tcol
    
    plt.plot(xVal, tcol, 'o')
    plt.savefig(figName)
    #plt.show()
   
  sys.exit()
  prjName = 'tva_980825'
  #prjName = 'tva_990715'
  if prjName == 'tva_980825':
    os.chdir('d:\\SCICHEM-2012\\Baldwin')
    preDbName1 = 'high_1_hr.csv.db'
    preDbName2 = 'kos2_km.smp.db'
    #preDbName2 = 'SCICHEM-01\\TVA_082598_55km.csv.db'
  #if prjName == 'tva_990715':
  #  os.chdir('d:\\SCICHEM-2012\\TVA_990715')
  #  preDbName1 = 'tva_990715.smp.db'
  #  preDbName2 = 'SCICHEM-01\\071599_vo3_lin_intel.smp.db'
 
  # Predicted data
  preConn1 = sqlite3.connect(preDbName1)
  preConn1.row_factory = sqlite3.Row
  preCur1 = preConn1.cursor()

  # Predicted data
  preConn2 = sqlite3.connect(preDbName2)
  preConn2.row_factory = sqlite3.Row
  preCur2 = preConn2.cursor()
  
  varNames = ["SO2", "O3", "NOx",  "NOy"]

  if prjName == "tva_990715":
    distance = [16] #[16, 62, 106]
    times    = [11.5]#[11.5, 12.5, 17.0]
    zSmp     = [415]#[415, 584, 582]

  if prjName == "tva_980825":
    distance = [55] #[20, 55, 110]
    times    = [12] #[12, 12.75, 14.5]
    zSmp     = [600] #[520, 600, 620]

  preQry2 = 'select Max(C001), Max(C002) , Max(C003) from dataTable'
  preQry1 = 'select Stack, Conc from dataTable'
  
  preArray1 = utilDb.db2Array(preCur1,preQry1)
  print preArray1[7:,1]

  preArray2 = utilDb.db2Array(preCur2,preQry2)
  print preArray2[0]*1000000
  print len(preArray1)
  a = (25, 32, 34, 20, 25, 20, 35, 30, 35, 27)
  plotBarGraph(preArray1[7:,1], preArray2[0]*1000000 )


  ######## 3 Hour Max ###############
 
  hrMaxQry3 = 'select C001, C002 , C003 from dataTable order by T'  
  hrMax3 = utilDb.db2Array(preCur2,hrMaxQry3)
  max_3_hr = [0.0,0.0,0.0]
  print 'three hr max', len(hrMax3)
  for i in range(0,len(hrMax3)-2,3):
    for j in range(0,3):
          curVal =  (hrMax3[i,j]+ hrMax3[i+1,j]+ hrMax3[i+2,j])/3
          #print 'curVal ' , curVal, 'maxVal ' , max_3_hr[j]
          if (curVal > max_3_hr[j]):
             #print 'Replacing ' ,  max_3_hr[j] , 'with ' , curVal
             max_3_hr[j] = curVal
          
  print max_3_hr
  plotBarGraph(max_3_hr, preArray2[0] )
  print 'three hr max done'

  

  #sys.exit()
  
 
  preConn1.close()
  preConn2.close()
      


def plotBarGraph(preArr1, preArr2):
  N = len(preArr1)

  ind = np.arange(N)  # the x locations for the groups
  width = 0.35       # the width of the bars

  fig = plt.figure()
  ax = fig.add_subplot(111)
  rects1 = ax.bar(ind, preArr1, width, color='r')

  
  
  rects2 = ax.bar(ind+width, preArr2, width, color='y')

  # add some
  ax.set_ylabel('Max Concentration')
  ax.set_title('Comparision plot')
  ax.set_xticks(ind+width)
  ax.set_xticklabels( ('Stack1', 'Stack2', 'Stack3') )

  ax.legend( (rects1[0], rects2[0]), ( 'AERMOD', 'SCIPUFF') )

  def autolabel(rects):
      # attach some text labels
      for rect in rects:
          height = rect.get_height()
          ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                  ha='center', va='bottom')

  autolabel(rects1)
  autolabel(rects2)

  plt.show()
              
# Main program
if __name__ == '__main__':
  mainProg()

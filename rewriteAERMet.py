
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
  os.chdir('D:\\SCICHEM-2012\\kinso2\\SCICHEM')
  #os.chdir('D:\\SCIPUFF\\runs\\EPRI\\aermod\\kinso2\\SCICHEM')
  #os.chdir('v:\\scipuff\\runs\\EPRI\\wainwright')
  #dataFile = '2009-10.SFC'
  dataFile = 'kinso2.sfc'
  colNames = ('year','month','day','j_day','hour',\
              'H','u','w','VPTG','Zic','Zim','L','Zo','Bo','r',\
              'Ws','Wd','zref','temp','ztemp','col1','col2')
  #   9,   9,      1,    244    1,\
  # -40.9,  0.755,  -9.000, -9.000, -999., 1510., 927.9, 0.1500, 6.00, 1.00,\
  #  7.57    173.0    7.9     287.1    2.0     0     0.80    66.     987.    10      ADJ-A1
  #sfcDat = np.loadtxt(dataFile,skiprows=1,dtype={'names':('year','month','day','j_day','hour',\
  #                         'H','u','w','VPTG','Zic','Zim','L','Zo','Bo','r',\
  #                         'Ws','Wd','zref','temp','ztemp','c1','c2','c3','c4','c5','c6'),\
  #                         'formats':('int','int','int','int','int','float','float','float','float','float',\
  #                         'float','float','float','float','float','float','float','float','float','float',\
  #                         'float','float','float','float','float','S20')})
  sfcDat = np.loadtxt(dataFile,skiprows=1,dtype={'names':colNames,\
                           'formats':('int','int','int','int','int','float','float','float','float','float',\
                           'float','float','float','float','float','float','float','float','float','float',\
                           'float','float')})
    
  #for colNo,colName in enumerate(colNames):
  #  print colNo,colName

  hr0 = sfcDat['j_day'][0] *24 + sfcDat['hour'][0]
  hr = sfcDat['j_day']*24 + sfcDat['hour'] - hr0
  print np.shape(sfcDat),hr0, hr,'\n'
  
  for colNo,colName in enumerate(colNames):
    if colNo in [0,1,2,3,4,20,21]:
      continue
    sfcMasked = ma.masked_where(sfcDat[colName] == -9.,sfcDat[colName])
    sfcMasked = ma.masked_where(sfcMasked == -999.,sfcMasked)
    sfcMasked = ma.masked_where(sfcMasked == -99999.0,sfcMasked)
    print colName,sfcMasked.min(),sfcMasked.max()
    figName = colName + '.png'
    plt.clf()
    plt.plot(hr, sfcMasked, 'o')
    plt.title('%s Min:%f Max:%f'%(colName,sfcMasked.min(),sfcMasked.max()))
    plt.savefig(figName)
    #plt.show()
    #ma.set_fill_value(sfcMasked, -999.0)
    sfcDat[colName] = ma.filled(sfcMasked,-999.0)

  sfcFile = open('new_' + dataFile,'w')
  for row in range(len(sfcDat)):
    for colNo,colName in enumerate(colNames):
      if colName in ['year','month','day','j_day','hour']:
        sfcFile.write('%03d '%sfcDat[colName][row])
      elif colNo < 25:
        sfcFile.write('%10.4f '%sfcDat[colName][row])
    sfcFile.write('\n')
  sfcFile.close()
   
# Main program
if __name__ == '__main__':
  mainProg()

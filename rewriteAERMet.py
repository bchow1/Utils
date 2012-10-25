
#!/bin/env python
import os
import sys
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import sqlite3
import time

# Local modules
sys.path.append('C:\\cygwin\\home\\sid\\python')
import utilDb

# Code for SCICHEM 2012 plots

def mainProg(dataFile):

  colNames = ''
  colFormats = ''

  if dataFile.lower().endswith('.sfc'):
    #   9,   9,      1,    244    1,\
    # -40.9,  0.755,  -9.000, -9.000, -999., 1510., 927.9, 0.1500, 6.00, 1.00,\
    #  7.57    173.0    7.9     287.1    2.0     0     0.80    66.     987.    10      ADJ-A1
    colNames = ('year','month','day','j_day','hour',\
                'H','u','w','VPTG','Zic','Zim','L','Zo','Bo','r',\
                'Ws','Wd','zref','temp','ztemp','col1','col2') # ,'c3','c4','c5','c6')
    colFormats = ('int','int','int','int','int','float','float','float','float','float',\
                  'float','float','float','float','float','float','float','float','float','float',\
                  'float','float') # ,'float','float','float','S20')

  if dataFile.lower().endswith('.pfl'):
    # 80  8 30  3  100.0 1  159.    8.99    20.2    4.3    0.12
    colNames = ('year','month','day','hour', 'height',\
                 'top', 'WDnn', 'WSnn', 'TTnn', 'SAnn', 'SWnn')
    colFormats = ('int','int','int','int','float', \
                    'int','float','float','float','float','float') 

  #for colNo,colName in enumerate(colNames):
  #  print colNo,colName
    
  metDat = np.loadtxt(dataFile,skiprows=1,dtype={'names':colNames,'formats':colFormats})
  print np.shape(metDat), '\n'

  # Set hr from 1st observation  
  timeTuple = time.strptime('%02d%02d%02d'%(metDat['year'][0],metDat['month'][0],metDat['day'][0]),"%y%m%d")
  epTime0 = time.mktime(timeTuple)
  epTime = np.zeros(len(metDat))
  for rowNo in range(len(metDat)):
    timeTuple = time.strptime('%02d%02d%02d'%(metDat['year'][rowNo],metDat['month'][rowNo],metDat['day'][rowNo]),"%y%m%d")
    epTime[rowNo] = time.mktime(timeTuple)
  hr = (epTime - epTime0)/3600.

  # set mask for not set values, plot masked values and fill with -999.0 
  for colNo,colName in enumerate(colNames):
    if colNo in [0,1,2,3,4,20,21]:
      continue
    sfcMasked = ma.masked_where(metDat[colName] == -9.,metDat[colName])
    sfcMasked = ma.masked_where(sfcMasked == -999.,sfcMasked)
    sfcMasked = ma.masked_where(sfcMasked == -999.9,sfcMasked)
    sfcMasked = ma.masked_where(sfcMasked == -99999.0,sfcMasked)
    if colName.lower() == "temp":
      sfcMasked = ma.masked_where(sfcMasked > 998.0,sfcMasked)
    if colName.lower() == "zo":
      sfcMasked = ma.masked_where(sfcMasked < 0.001,sfcMasked)
      sfcMasked = ma.filled(sfcMasked,0.01)
      

    if colName.lower() in ["wd","wdnn","sann"]:
      sfcMasked = ma.masked_where(sfcMasked > 360.0,sfcMasked)
    if colName.lower() in ["ws","wsnn"]:
      sfcMasked = ma.masked_where(sfcMasked > 998.0,sfcMasked)
    if colName.lower() == "swnn":
      sfcMasked = ma.masked_where(sfcMasked == 99.0,sfcMasked)
    if colName.lower() == "TTnn":
      sfcMasked = ma.masked_where(sfcMasked > 99.0,sfcMasked)
      sfcMasked = ma.masked_where(sfcMasked < -10.,sfcMasked)

    print colName,sfcMasked.min(),sfcMasked.max()

    figName = colName + '.png'
    plt.clf()
    plt.plot(hr, sfcMasked, 'o')
    plt.title('%s Min:%f Max:%f'%(colName,sfcMasked.min(),sfcMasked.max()))
    plt.savefig(figName)
    #plt.show()
    #ma.set_fill_value(sfcMasked, -999.0)
    metDat[colName] = ma.filled(sfcMasked,-999.0)

  # Write new data files
  
  sfcFile = open('new_' + dataFile,'w')
  if dataFile.lower().endswith('.sfc'):
      # (3(I2,1X), I3,1X, I2,1X, F6.1,1X, 2(F6.3,1X), F5.0,1X, F8.1,1X, F5.2,1X,
      # 2(F6.2,1X), F7.2,1X, F5.0, 5(1X,F6.1))
      s  = '{0[0]:2d} {0[1]:2d} {0[2]:2d} {0[3]:3d} {0[4]:2d} '
      s += '{0[5]:6.1f} {0[6]:6.3f} {0[7]:6.3f} {0[8]:5.0f} {0[9]:8.1f} '
      s += '{0[10]:5.2f} {0[11]:6.2f} {0[12]:6.2f} {0[13]:7.2f} {0[14]:6.1f} ' 
      s += '{0[15]:6.1f} {0[16]:6.1f} {0[17]:6.1f} {0[18]:6.1f} {0[19]:6.1f} '
      s += '{0[20]:6.1f}\n'
  if dataFile.endswith('.pfl'):
      # 4(I2,1X), F6.1,1X, I1,1X, F5.0,1X, F7.2,1X, F7.1, 1X,F6.1, 1X,F7.2
      s  = '{0[0]:2d} {0[1]:2d} {0[2]:2d} {0[3]:2d} {0[4]:6.1f} {0[5]:1d} {0[6]:5.0f} '
      s += '{0[7]:7.2f} {0[8]:7.1f} {0[9]:6.1f} {0[10]:7.2f}\n'
      
  for row in range(len(metDat)):
        sfcFile.write(s.format(metDat[row]))
        
  sfcFile.close()

# Main program
if __name__ == '__main__': 

  runDir = os.getcwd() 
  #runDir = 'D:\\SCICHEM-2012\\kinso2\\SCICHEM'
  #runDir = '/home/user/bnc/scipuff/runs/EPRI/wwright'
    
  dataFile = raw_input('AERMOD datafile name? ')
  #dataFile = '2009-10.SFC'
  #dataFile = 'kosovo11-ww-scipuff.sfc'
  #dataFile = 'kinso2.sfc'
  #dataFile = 'kinso2.pfl'

  os.chdir(runDir)
  mainProg(dataFile)

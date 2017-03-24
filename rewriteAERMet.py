
#!/bin/env python
import os
import sys
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import sqlite3
import time

# Local modules
#sys.path.append('C:\\cygwin\\home\\sid\\python')
sys.path.append('/home/user/bnc/python')
import utilDb

# Code for SCICHEM 2012 plots

def mainProg():

  #os.chdir('/home/user/bnc/scipuff/runs/EPRI/v3b3_Tests/Linux/so2_2005')
  if sys.argv.__len__() > 1:
    dataFile = sys.argv[1]
  else:
    #dataFile = 'KBOI_2005.SFC'
    dataFile = 'KBOI.2005.PFL'
  #os.chdir('D:\\SCIPUFF\\runs\\EPRI\\Lynne\\quatar')
  #dataFile = 'quatar.sfc'
  #os.chdir('D:\\SCIPUFF\\runs\\EPRI\\DES_NH\\140905')
  #dataFile = 'Concord2008v2.SFC'
  #os.chdir('D:\\SCIPUFF\\runs\\EPRI\\aermod\\kinso2\\SCICHEM')
  #dataFile = 'kinso2.sfc'
  #dataFile = 'kinso2.pfl'
  #os.chdir('/home/user/bnc/scipuff/runs/EPRI/wwright')

  colNames = ''
  colFormats = ''

  if dataFile.lower().endswith('.sfc'):
    colNames = ('year','month','day','j_day','hour',\
                'H','u','w','VPTG','Zic','Zim','L','Zo','Bo','r',\
                'Ws','Wd','zref','temp','ztemp','col1','col2','col3')
    colFormats = ('int','int','int','int','int','float','float','float','float','float',\
                  'float','float','float','float','float','float','float','float','float','float',\
                  'float','float','float')
  #   9,   9,      1,    244    1,\
  # -40.9,  0.755,  -9.000, -9.000, -999., 1510., 927.9, 0.1500, 6.00, 1.00,\
  #  7.57    173.0    7.9     287.1    2.0     0     0.80    66.     987.    10      ADJ-A1
  #sfcDat = np.loadtxt(dataFile,skiprows=1,dtype={'names':('year','month','day','j_day','hour',\
  #                         'H','u','w','VPTG','Zic','Zim','L','Zo','Bo','r',\
  #                         'Ws','Wd','zref','temp','ztemp','c1','c2','c3','c4','c5','c6'),\
  #                         'formats':('int','int','int','int','int','float','float','float','float','float',\
  #                         'float','float','float','float','float','float','float','float','float','float',\
  #                         'float','float','float','float','float','S20')})

  if dataFile.lower().endswith('.pfl'):
    colNames = ('year','month','day','hour', 'height',\
                 'top', 'WDnn', 'WSnn', 'TTnn', 'SAnn', 'SWnn')
    #80  4  3  1   10.0 0 -999.    4.90     9.9 -999.0 -999.00
    colFormats = ('int','int','int','int','float', \
                    'int','float','float','float','float','float') 
    

  #  year, month, day , hour, height, top, WDnn, WSnn, TTnn, SAnn, SWnn
  # FORMAT (4(I2,1X), F6.1,1X, I1,1X, F5.0,1X, F7.2,1X, F7.1, 1X,F6.1, 1X,F7.2)
  # 80  8 30  3  100.0 1  159.    8.99    20.2    4.3    0.12

  sfcDat = getDataFromFile(dataFile, colNames, colFormats)

  #for colNo,colName in enumerate(colNames):
  #  print colNo,colName
  timeTuple = time.strptime('%02d%02d%02d'%(sfcDat['year'][0],sfcDat['month'][0],sfcDat['day'][0]),"%y%m%d")
  epTime0 = time.mktime(timeTuple)
  epTime = np.zeros(len(sfcDat))
  for rowNo in range(len(sfcDat)):
    timeTuple = time.strptime('%02d%02d%02d'%(sfcDat['year'][rowNo],sfcDat['month'][rowNo],sfcDat['day'][rowNo]),"%y%m%d")
    epTime[rowNo] = time.mktime(timeTuple)
  hr =   (epTime - epTime0)/3600.
  print np.shape(sfcDat), '\n' #,hr0, hr,'\n'
  
  for colNo,colName in enumerate(colNames):
    if colNo in [0,1,2,3,4,20,21]:
      continue
    sfcMasked = ma.masked_where(sfcDat[colName] == -9.,sfcDat[colName])
    sfcMasked = ma.masked_where(sfcMasked == -999.,sfcMasked)
    sfcMasked = ma.masked_where(sfcMasked == -999.9,sfcMasked)
    sfcMasked = ma.masked_where(sfcMasked == -99999.0,sfcMasked)
    if colName == "TTnn":
      sfcMasked = ma.masked_where(sfcMasked > 99.0,sfcMasked)
      sfcMasked = ma.masked_where(sfcMasked < -10.,sfcMasked)
    if colName == "temp" or colName == "Wd" or colName == "Ws":
      sfcMasked = ma.masked_where(sfcMasked == 999.0,sfcMasked)     
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
  if dataFile.lower().endswith('.sfc'):
      # (3(I2,1X), I3,1X, I2,1X, F6.1,1X, 2(F6.3,1X), F5.0,1X, F8.1,1X, F5.2,1X,
      # 2(F6.2,1X), F7.2,1X, F5.0, 3(1X,F6.1))
      s  = '{0[0]:2d} {0[1]:2d} {0[2]:2d} {0[3]:3d} {0[4]:2d} {0[5]:6.1f} '
      s += '{0[6]:6.3f} {0[7]:6.3f} {0[8]:5.0f} {0[9]:8.1f} {0[10]:5.2f} {0[11]:6.2f} {0[12]:13.4e} '
      s += '{0[13]:7.2f} {0[14]:6.1f} {0[15]:6.1f} {0[16]:6.1f} {0[17]:6.1f} {0[18]:6.1f} {0[19]:6.1f} {0[20]:6.1f}\n'
  if dataFile.lower().endswith('.pfl'):
      # 4(I2,1X), F6.1,1X, I1,1X, F5.0,1X, F7.2,1X, F7.1, 1X,F6.1, 1X,F7.2
      s  = '{0[0]:2d} {0[1]:2d} {0[2]:2d} {0[3]:2d} {0[4]:6.1f} {0[5]:1d} {0[6]:5.0f} '
      s += '{0[7]:7.2f} {0[8]:7.1f} {0[9]:6.1f} {0[10]:7.2f}\n'         
  print colNames
  for row in range(len(sfcDat)):
    outLine = s.format(sfcDat[row])
    if sfcDat[row] == sfcDat[0] or sfcDat[row] == sfcDat[-1]:
      sys.stdout.write(outLine)
    sfcFile.write(outLine)       
  sfcFile.close()


def getDataFromFile(dataFile, colNames, colFormats):
  print colNames , '\n'
  print colFormats, '\n'
  colNos = [i for i in range(len(colNames))]
  sfcDat = np.loadtxt(dataFile,skiprows=1,dtype={'names':colNames,'formats':colFormats},usecols=colNos)
  return sfcDat
   
# Main program
if __name__ == '__main__':
  
  #s = '{0[0]:2d} {0[1]:2d} {0[2]:2d} {0[3]:2d} {0[4]:6.1f} {0[5]:1d} {0[6]:5.0f} {0[7]:7.2f} {0[8]:7.1f} {0[9]:6.1f} {0[10]:7.2f}'
  #sfcDat = [80, 4,  3,  1,   10.0, 0, -999.,    4.90,     9.9, -999.0, -999.00]
  #print s.format(sfcDat)
  
  #s = '{:04d} {:03d}'
  # sfcDat = [10,80]
  #print  '{0[0]:+6.3f}; {0[1]:+6.2f}'.format(sfcDat)#(10, 80)
  
  #coord = (3, 5)
  #print 'X: {0[0]};  Y: {0[1]}'.format(coord)

  #print '{0[0]:6.3f};  Y: {0[1]:5.0f}'.format(sfcDat)
  #print '{0[0]}; {:+f}'.format(sfcDat)  # show it always
  
  mainProg()

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.cm as cm
from matplotlib import colors

if sys.platform == 'win32':
  os.chdir('d:\\SCIPUFF\\runs\\AFTAC\\newMexico')
else:
  os.chdir('/home/user/bnc/scipuff/runs/AFTAC/newMexico_puffIds')

hdr = "t,p1%idtl,p1%xbar,p1%ybar,p1%zbar,p1%sxx,p1%syy,p1%szz,p1%c,p1%cc,p1%si2,p1%zi,p1%zc,pvol"
colNames = hdr.replace('p1%','').split(',')
colDtypes = {}
for colName in colNames:
  if colName == 'idtl':
    colDtypes.update({'i':np.int})
  else:
   colDtypes.update({'i':np.float})
print colNames       
#colNames  = ['i','j','k','np','volI','volJ','vRat']    
#colDtypes = {'i':np.int,'j':np.int,'k':np.int,'np':np.int,'volI':np.float,'volJ':np.float,'vRat':np.float}

  
for hr in [2]:
   
  csvName = 'Hr%d_CellVol.csv'%hr
  df = pd.read_csv(csvName, sep=',', skiprows=0, comment='#', dtype=colDtypes, names=colNames)
  #print df
  puffI = df[0:-1]
  #print 'puffI: ',puffI
  puffS = df.tail(n=1)
  #print 'puffS: ',puffS
  
  print 'Max mass    = ',puffI['c'].max(),puffS['c'].values[0]
  print 'Max vol.    = ',puffI['pvol'].max(),puffS['pvol'].values[0]
  

  massMax = df['c'].max()
  volMax  = df['pvol'].max()
  df['c']    = df['c']/massMax
  df['pvol'] = df['pvol']/volMax
  
  print '\nAfter Scaling:'
  print 'Max mass    = ',puffI['c'].max(),puffS['c'].values[0]
  print 'Max vol.    = ',puffI['pvol'].max(),puffS['pvol'].values[0]
  print 'Summed vol. = ',puffI['pvol'].sum(),puffS['pvol'].values[0]
  
  clrlev = 6
  vmin = 1e-3
  vmax = 1.
   
  #levels = np.linspace(vmin,vmax,num=clrlev)
  #clrmap = cm.get_cmap('jet',clrlev-1)
  #lnorm  = colors.Normalize(levels,clip=False)
 
  levels = np.logspace(vmin,vmax,num=clrlev,base=10.0)
  clrmap = cm.get_cmap('jet',clrlev-1)
  lnorm  = colors.LogNorm(levels,clip=False)
   
  fig = plt.figure()
  plt.clf()
  plt.hold(True)
  plt.setp(plt.gca(), frame_on=False, xticks=(), yticks=())
  ps = 500
  
  axy = fig.add_subplot(2,2,1) 
  cs = axy.scatter(puffI['xbar'],puffI['ybar'],c=puffI['c'],s=puffI['pvol']*ps,marker='o',\
                   vmin=vmin,vmax=vmax,norm=lnorm,cmap=clrmap)
  axy.scatter(puffS['xbar'],puffS['ybar'],c=puffS['c'],s=puffS['pvol']*ps,marker='s',\
                   vmin=vmin,vmax=vmax,norm=lnorm,cmap=clrmap)
  axy.set_xlabel('x')
  axy.set_ylabel('y')
  plt.setp(plt.gca(),xticks=(),yticks=())
  plt.colorbar(cs)
  
  
  axz = fig.add_subplot(2,2,3) 
  cs = axz.scatter(puffI['xbar'],puffI['zbar'],c=puffI['c'],s=puffI['pvol']*ps,marker='o',\
                   vmin=vmin,vmax=vmax,norm=lnorm,cmap=clrmap)
  axz.scatter(puffS['xbar'],puffS['zbar'],c=puffS['c'],s=puffS['pvol']*ps,marker='s',\
                   vmin=vmin,vmax=vmax,norm=lnorm,cmap=clrmap)
  axz.set_xlabel('x')
  axz.set_ylabel('z')
  plt.setp(plt.gca(),xticks=(),yticks=())
  
  ayz = fig.add_subplot(2,2,4) 
  cs = ayz.scatter(puffI['ybar'],puffI['zbar'],c=puffI['c'],s=puffI['pvol']*ps,marker='o',\
                   vmin=vmin,vmax=vmax,norm=lnorm,cmap=clrmap)
  ayz.scatter(puffS['ybar'],puffS['zbar'],c=puffS['c'],s=puffS['pvol']*ps,marker='s',\
                   vmin=vmin,vmax=vmax,norm=lnorm,cmap=clrmap)
  ayz.set_xlabel('y')
  plt.setp(plt.gca(),xticks=(),yticks=())
  
  #plt.title('Hr %d'%hr)
  plt.hold(False)
  plt.show()
  #plt.savefig('Hr%d.png'%hr)




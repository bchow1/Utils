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
  
colNames = ['i','j','k','np','volI','volJ','vRat']    
colDtype = {'i':np.int,'j':np.int,'k':np.int,'np':np.int,'volI':np.float,'volJ':np.float,'vRat':np.float}

  
for hr in [1,2,3]:
   
  csvName = 'Hr%d_Pvol.csv'%hr
  df = pd.read_csv(csvName, sep=',', skiprows=1, comment='#', dtype=colDtype, names=colNames)
  #print df.columns
  
  clrlev = 6
  vmin = df['vRat'].min()
  vmax = df['vRat'].max()
  print vmin, vmax
   
  levels = np.linspace(vmin,vmax,num=clrlev)
  clrmap = cm.get_cmap('jet',clrlev-1)
  lnorm  = colors.Normalize(levels,clip=False)
 
  #levels = np.logspace(1e-5,1,num=clrlev,base=10.0)
  #clrmap = cm.get_cmap('jet',clrlev-1)
  #lnorm  = colors.LogNorm(levels,clip=False)
   
   
  plt.clf()
  cs = plt.scatter(df['vRat'],df['k'],marker='o')
  #plt.scatter(df['vRat'],df['k'],c=df['vRat']/vmax,edgecolors='none',marker='o',\
  #            vmin=vmin,vmax=vmax,norm=lnorm,cmap=clrMap)
  plt.ylabel('k')
  plt.xlabel('Vol Ratio')
  plt.title('Hr %d'%hr)
  #plt.colorbar(cs,ticks=[vmin,vmax])
  #plt.show()
  plt.savefig('Hr%d.png'%hr)




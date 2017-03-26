#
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.ticker as mtick
from matplotlib import colors
from matplotlib.mlab import griddata

postFile = 'conc_avg_168hr.plt'
pltContour = False
nx = 32
ny = 32
logBase = 10

#colNames = " X             Y      AVGCONC    ZELEV    ZHILL    ZFLAG    AVE     GRP       DATE     NETID".split()
colNames = "X Y AvgConc Date".split()
useCols  = [1,2,3,9]

allConc = pd.read_csv(postFile,names=colNames,delim_whitespace=True,skiprows=8,usecols=useCols)
print allConc.head()

maxConc = allConc['AvgConc'].max()
print maxConc

times = allConc['Date'].unique()
print len(times), times

xy = allConc[allConc['Date']==times[0]][['X','Y']]
print len(xy),xy.values

if pltContour:
  xGrd = xy['X'].values
  yGrd = xy['Y'].values
  xMin = min(xGrd)
  xMax = max(xGrd)
  yMin = min(yGrd)
  yMax = max(yGrd)

  x  = np.linspace(xMin, xMax, num=nx)
  y  = np.linspace(yMin, yMax, num=ny)
  dx = 0.1*(xMax-xMin)
  dy = 0.1*(yMax-yMin)

  X, Y = np.meshgrid(x,y)

  clrmax = int(np.log10(maxConc) + 1)
  clrmin = clrmax - 7
  clrlev = (clrmax - clrmin + 1)
  levels = np.logspace(clrmin,clrmax,num=clrlev,base=logBase)
  clrmap = cm.get_cmap('jet',clrlev-1)
  lnorm  = colors.LogNorm(levels,clip=False)

  for it,tm in enumerate(times):
    #fig = plt.figure(1,frameon=False)
    plt.clf()
    plt.hold(True)
    #ax = fig.add_subplot(111)
    #
    cGrd = allConc[allConc['Date']==tm]['AvgConc'].values
    C = griddata(xGrd, yGrd, cGrd, x, y)
    C = np.ma.masked_where(C<= 0, C)
    cset1 = plt.contour (X, Y, C, levels, norm=lnorm, linewidths=0.5, colors='k') 
    cset2 = plt.contourf(X, Y, C, levels, norm=lnorm, cmap=clrmap)
    plt.xlim(xMin-dx,xMax+dx)
    plt.ylim(yMin-dy,yMax+dy)
    plt.xlabel('Longitude')
    #plt.setp(ax.get_xticklabels(),fontsize=8)
    plt.ylabel('Latitude')
    plt.title('Concentrations for Week '+ '%d (ug/m3)'%(it+1))
    cax = plt.axes([0.91,0.1,0.02,0.8])
    cbar = plt.colorbar(cset2,cax=cax,ticks=levels,format='%.1E')
    cbar.ax.tick_params(labelsize=8)
    #plt.show()
    fName = 'Week%03d'%it + '.png'
    plt.hold(False)
    plt.savefig(fName)
    print it,tm
    #if it == 10:
    #break

iMax = allConc['AvgConc'].idxmax()
print 'iMax = ',iMax
maxConcRow = allConc.ix[iMax]
maxSmp = allConc[(allConc['X'] == maxConcRow['X']) & (allConc['Y'] == maxConcRow['Y'])]
maxSmp['Wk'] = [i for i in range(len(maxSmp))]
print maxSmp.head()

#fig = plt.figure(1,frameon=False)
fig = plt.figure()
ax = fig.add_subplot(111)
plt.hold(True)
ax.plot(maxSmp['Wk'].values,maxSmp['AvgConc'].values)
ax.set_title('Concentration at (%6.2f, %6.2f)'%(maxConcRow['X'],maxConcRow['Y']))
ax.set_xlabel('Week')
ax.set_ylabel('ug/m3')
ax.set_xlim([0,len(maxSmp)])
ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
plt.setp(ax.get_xticklabels(),fontsize=9)
plt.setp(ax.get_yticklabels(),fontsize=9)
#ax.ticklabel_format(style='sci',axis='y',useOffset=False,scilimits=(-1,5))
plt.hold(False)
plt.savefig('Conc1_Time.png')
#plt.show()

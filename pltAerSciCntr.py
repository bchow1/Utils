import os
import sys
import socket
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from matplotlib import colors
import matplotlib.cm as cm

# Local libs
import tab2db
import utilDb
import utilPlot

# 
# This module reads kincaid output files from AERMOD, SCICHEM and SCIPUFF(HPAC)
# and plots the contours. The domain limits and origin  are currently hard coded
# for kinsf6 case of 072480. joinPDF does not work for Windows as subprocess cannot
# find gs from cygwin !!!


compName = socket.gethostname()

# Local modules
if  compName == 'pj-linux4':
  sys.path.append('/home/user/bnc/python')
  runDir = ''
else:
  runDir = 'D:\\Aermod\\v12345\\runs\\kinsf6'
os.chdir(runDir)

# Find x,y locations for obs
xyObs = utilDb.db2Array('OBS_CONC\\KINSF6.SUM.db','select recx,recy from datatable group by recx,recy')
xyObs[:,0] = xyObs[:,0] - 200. 
xyObs[:,1] = xyObs[:,1] - 4000. 
xObsMin,xObsMax = xyObs[:,0].min(),xyObs[:,0].max()
yObsMin,yObsMax = xyObs[:,1].min(),xyObs[:,1].max()

# Create db for the AERMOD post file
#tab2db.makeDb('AERMOD\\KSF6-724.80S',comment='*',hdrlno=7,collist='1,2,3,9')
hrArry = utilDb.db2Array('AERMOD\\KSF6-724.80S.db','select distinct grp from datatable',dim=1)
xyAer  = utilDb.db2Array('AERMOD\\KSF6-724.80S.db','select x,y from datatable group by x,y')
xyAer  = xyAer*1e-3  # m to km
xAerMin,xAerMax = xyAer[:,0].min(),xyAer[:,0].max()
yAerMin,yAerMax = xyAer[:,1].min(),xyAer[:,1].max()

#levels = [0,2,5,10,20,30,50,100,125,150,200,300]
#clrmap = cm.get_cmap('gist_ncar_r',len(levels)-1)
#lnorm  = colors.Normalize(levels,clip=False)

levels = np.logspace(-2,9,num=12,base=2.0)
clrmap = cm.get_cmap('jet',len(levels)-1)
lnorm  = colors.LogNorm(levels,clip=False)
print levels
#
params1 = {'axes.labelsize': 10, 'text.fontsize': 10, 'xtick.labelsize': 10,
           'ytick.labelsize': 10, 'legend.pad': 0.1,  # empty space around the legend box
           'legend.fontsize': 14, 'lines.markersize': 6, 'lines.width': 2.0,
           'font.size': 12}

plt.rcParams.update(params1)
fList = []

for hr in hrArry:
  
  hrStr = str(hr)
  
  iHr = int(hrStr[6:8]) 
  if iHr < 5 or iHr > 16:
    continue

  print '\n Plotting for %s'%hrStr
  
  fig = plt.figure(figsize=(8,11), dpi=100)
  #fig = plt.figure()
  fig.clf()
  fig.hold(True)
  ax = fig.add_subplot(1,1,1)
  plt.text(0.2,1.05,'Max 1 hr avg. conc for hr %s'%hrStr,weight='bold',fontsize=14)
  plt.text(0.5,-0.09,'X(km)',transform=ax.transAxes,fontsize=12)
  plt.text(-0.15,0.5,'Y(km)',transform=ax.transAxes,rotation='vertical',fontsize=12)
  plt.setp(plt.gca(), frame_on=False, xticks=(), yticks=())
  
  # Plot Observations 
  ax = fig.add_subplot(3,1,1)
  cObsMax = 0.
  obsStr = 'select recx,recy,CHI from datatable where yy=%s and mm = %s and dd = %s and hh=%s'%(hrStr[0:2],hrStr[2:4],hrStr[4:6],hrStr[6:8])
  obsArray = utilDb.db2Array('OBS_CONC\\KINSF6.SUM.db',obsStr)
  if len(obsArray) > 0:
    cObs = obsArray[:,2] + 1.e-4
    cObsMax = cObs.max()
    if cObsMax > 1.e-4:
      x = obsArray[:,0] - 200.
      y = obsArray[:,1] - 4000.
      print 'Observed max conc = %g'%(cObsMax)
      triangles = tri.Triangulation(x, y)
      CS   = plt.tricontour(x, y, cObs, 15, linewidths=0.5, colors='k')
      CS   = plt.tricontourf(x, y, cObs, 15, norm= lnorm, levels=levels, cmap=clrmap)
      cbar = plt.colorbar(ticks=levels,format='%5.1e') # draw colorbar
      cl   = plt.getp(cbar.ax, 'ymajorticklabels')
      plt.setp(cl, fontsize=7)
    else:
      plt.scatter(xyObs[:,0],xyObs[:,1],marker='o',c='b',s=5,zorder=10)
  else:
    # plot data points.
    plt.scatter(xyObs[:,0],xyObs[:,1],marker='o',c='b',s=5,zorder=10)
  ax.set_xlim([60.,100.])
  ax.set_ylim([380.,410.])
  ax.text(0.02,0.9,'Observed',transform=ax.transAxes,fontsize=9)
  ax.text(0.8,0.9,'Cmax=%5.0f'%cObsMax,transform=ax.transAxes,fontsize=8)
  
  # Plot Aermod output 
  ax = fig.add_subplot(3,1,2)
  cAerMax = 0.
  aerArray =utilDb.db2Array('AERMOD\\KSF6-724.80S.db','select x,y,average from datatable where grp = %d'%hr)
  if len(aerArray)> 0.:
    cAer = aerArray[:,2]*167. + 1.e-4 # Convert ug/m3 to ppt for SF6
    cAerMax = cAer.max()
    print 'AERMOD max conc = %g'%(cAerMax)
    if cAerMax > 1.e-4:
      x = aerArray[:,0]*1e-3
      y = aerArray[:,1]*1e-3  
      triangles = tri.Triangulation(x, y)
      CS = plt.tricontour(x, y, cAer, 15, linewidths=0.5, colors='k')
      CS = plt.tricontourf(x, y, cAer, 15, norm= lnorm, levels=levels, cmap=clrmap)
      cbar = plt.colorbar(ticks=levels,format='%5.1e') # draw colorbar
      cl   = plt.getp(cbar.ax, 'ymajorticklabels')
      plt.setp(cl, fontsize=7)      
    else:
      plt.scatter(xyAer[:,0],xyAer[:,1],marker='o',c='b',s=5,zorder=10)
  else:
    # plot data points.
    plt.scatter(xyAer[:,0],xyAer[:,1],marker='o',c='b',s=5,zorder=10)
  ax.text(0.02,0.9,'AERMOD',transform=ax.transAxes,fontsize=9)
  ax.text(0.8,0.9,'Cmax=%5.0f'%cAerMax,transform=ax.transAxes,fontsize=8)
  ax.set_xlim([60.,100.])
  ax.set_ylim([380.,410.])
  
  # Plot SCIPUFF output 
  ax = fig.add_subplot(3,1,3)
  cSciMax  = 0.
  #sciArray = utilDb.db2Array('SCICHEM\\KSF6-724_80I.smp.db','select xSmp,ySmp,value from samtable a, smptable p where a.colno=p.colno and varname = "C" and time = %d'%(iHr-0))
  sciArray = utilDb.db2Array('SCICHEM\\072480_new.smp.db','select xSmp,ySmp,value from samtable a, smptable p where a.colno=p.colno and varname = "C" and time = %d'%(iHr-5))
  if len(sciArray)> 0.:
    cSci = sciArray[:,2]*167.*1.e9 + 1.e-4 # Convert kg/m3 to ppt for SF6
    cSciMax = cSci.max()
    print 'SCIPUFF max conc = %g'%(cSciMax)
    if cSciMax > 1.e-4:
      x = sciArray[:,0] - 200.
      y = sciArray[:,1] - 4000.  
      triangles = tri.Triangulation(x, y)
      CS = plt.tricontour(x, y, cSci, 15, linewidths=0.5, colors='k')
      CS = plt.tricontourf(x, y, cSci, 15, norm= lnorm, levels=levels, cmap=clrmap)
      cbar = plt.colorbar(ticks=levels,format='%5.1e') # draw colorbar
      cl   = plt.getp(cbar.ax, 'ymajorticklabels')
      plt.setp(cl, fontsize=7)      
    else:
      plt.scatter(xyAer[:,0],xyAer[:,1],marker='o',c='b',s=5,zorder=10)
  else:
    # plot data points.
    plt.scatter(xyAer[:,0],xyAer[:,1],marker='o',c='b',s=5,zorder=10)
  ax.text(0.02,0.9,'SCIPUFF',transform=ax.transAxes,fontsize=9)
  ax.text(0.8,0.9,'Cmax=%5.0f'%cSciMax,transform=ax.transAxes,fontsize=8)
  ax.set_xlim([60.,100.])
  ax.set_ylim([380.,410.])
  
  fig.hold(False)
  #plt.show()
  fName = '%s.pdf'%hr
  plt.savefig(fName)
  fList.append(fName)
  
#utilPlot.joinPDF(fList,'SCICHEM_072480.pdf')
print 'Done'
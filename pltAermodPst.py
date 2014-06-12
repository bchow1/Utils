#!/bin/python

import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import matplotlib.cm as cm
import matplotlib.colors as colors

#pstFile  = 'GIBSON01.PST'
pstFile   = 'vertCross.pst'
addSrcLoc = False

if addSrcLoc:
  srcList = []
  srcList.append([432999.8,4247188.6,119.00])
  srcList.append([432999.8,4247188.6,119.00])
  srcList.append([432923.7,4247251.3,118.49])
  srcList.append([432886.1,4247339.5,117.93])
  srcList.append([432831.3,4247423.2,116.30])
  srcList.append([432424.0,4250202.0,119.00]) # MtCarmel
  srcList.append([434654.0,4249666.0,119.30]) # EastMountCarmel
  srcList.append([427174.9,4247181.5,138.00]) # Shrodt
  srcList.append([434791.6,4246296.0,119.00]) # Gibson

  srcA = np.array(srcList)
  print srcA

# Load PST file
cnc   = np.loadtxt(pstFile,skiprows=8,usecols=(0,1,2,3,8))
nCol  = cnc.shape[1]
zList = np.unique(cnc[:,3])
hList = np.unique(cnc[:,4])
cMax  = cnc[:,2].max()
print np.shape(cnc),zList,cMax,cnc[:,2].min()

# set Levels
isLinear = True
if isLinear:
    num   = 11
    vmin  = 0.0
    vmax  = 1000.0
    levels = np.linspace(vmin,vmax,num=num)
    lnorm  = colors.Normalize(levels,clip=False)
else:
    num  = 7
    vmax = 3  # int(np.log10(maxC)) + 1
    vmin = -3 # vmax - num + 1
    levels = np.logspace(vmin,vmax,num=num,base=10.0)
    lnorm  = colors.LogNorm(levels,clip=False)
clrmap = plt.cm.get_cmap('jet',len(levels)-1)
print levels

'''
for z in zList: # [0,200]: 
  zflag = np.repeat(cnc[:,3]==z,nCol).reshape(np.shape(cnc))
  cxy = np.extract(zflag,cnc).reshape(-1,nCol)
  for hr in range(9042323,9042324): #hList:
    hflag = np.repeat(cxy[:,4]==hr,nCol).reshape(np.shape(cxy))
    #print np.shape(hflag),hflag
    chr = np.extract(hflag,cxy).reshape(-1,nCol)
    print 'Hour: ',hr,z,np.shape(chr),chr[:,2].max(),chr[:,2].min()
    if chr[:,2].max() < 0.1:
      continue
    x = chr[:,0]
    y = chr[:,1]
    C = chr[:,2] + 10**(vmin-1)
    cm = np.ma.array(chr, mask=np.repeat(chr[:,2] < 10**vmin, chr.shape[1])).compressed().reshape(-1,chr.shape[1])
    #print cm
    #print hr,z,np.shape(cm),cm[:,2].max(),cm[:,2].min(),10**vmin,10**vmax
    plt.clf()
    plt.hold(True)
    #
    triangles = tri.Triangulation(x, y)
    CS   = plt.tricontour(x, y, C, 15, norm = lnorm, levels=levels,linewidths=0.5, colors='k')
    CS   = plt.tricontourf(x, y, C, 15, norm= lnorm, levels=levels, cmap=clrmap, vmin=10.**vmin)
    CS.set_clim(10.**vmin,10.**vmax)
    CS.cmap.set_under('white')

    #for ip in range(0,len(chr)):
    #  if cm[ip,2] > 1.0:
    #    print ip,cm[ip,0],cm[ip,1],'%4.2f'%(cm[ip,2])
    #    plt.text(cm[ip,0],cm[ip,1],'%4.2f'%(cm[ip,2]),fontsize=9)
    #    cs = plt.scatter(cm[ip,0],cm[ip,1],c=cm[ip,2],marker='o',s=50,vmin=10.**vmin,vmax=10.**vmax,norm=lnorm,cmap=clrmap)
    
    #cs = plt.scatter(cm[:,0],cm[:,1],c=cm[:,2],marker='o',s=20,vmin=10.**vmin,vmax=10.**vmax,norm=lnorm,cmap=clrmap)
    #cs.set_clim(10.**vmin,10.**vmax)
    
    cbar = plt.colorbar(ticks=levels,format='%5.1e') # draw colorbar    
    
    if addSrcLoc:
      plt.scatter(srcA[:,0],srcA[:,1],marker='*')
    
    plt.title('z = %dm, Hr = %d'%(z,int(hr)-9042300))
    plt.hold(False)
    plt.savefig('C_%dm_%dhr.png'%(z,int(hr)-9042300))
    #plt.show()
'''

for hr in range(9042323,9042324):
  hflag = np.repeat(cnc[:,4]==hr,nCol).reshape(cnc.shape)
  cxz   = np.extract(hflag,cnc).reshape(-1,nCol)
  print np.shape(hflag),hflag
  x = cxz[:,0]/1000.
  z = cxz[:,3]
  C = cxz[:,2] + 10**(vmin-1)
  plt.clf()
  plt.hold(True)
  #
  triangles = tri.Triangulation(x, z)
  CS = plt.tricontour(x, z, C, 15, norm = lnorm, levels=levels,linewidths=0.5, colors='k')
  
  if isLinear:
    CS = plt.tricontourf(x, z, C, 15, norm= lnorm, levels=levels, cmap=clrmap, vmin=vmin)
    CS.set_clim(vmin,vmax)
  else:
    CS = plt.tricontourf(x, z, C, 15, norm= lnorm, levels=levels, cmap=clrmap, vmin=10.**vmin)
    CS.set_clim(10.**vmin,10.**vmax)

  CS.cmap.set_under('white')  
  cbar = plt.colorbar(ticks=levels,format='%5.1e') # draw colorbar    
  plt.title('Conc (ug/m3) for Hr = %d'%(int(hr)-9042300))
  plt.xlabel('X(km)')
  plt.ylabel('Z(m)')
  plt.hold(False)
  plt.savefig('AER_cslice_%dhr.png'%(int(hr)-9042300))
  #plt.show()
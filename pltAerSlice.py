#!/bin/python
import os
import subprocess
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import matplotlib.colors as colors

# cmd /K D:\Python27\python.exe "$(FULL_CURRENT_PATH)"
os.chdir("D:\\SCIPUFF\\runs\\EPRI\\AECOM\\Gibson\\SCICHEM\\Gibson_4Days")
aermod = 'd:\\Aermod\\v12345\\workspace\\Debug\\AERMOD.exe'
rmOut = True

#
# Vertical Slice
#

#Source
x1 = 432.8313
y1 = 4247.4232

# Receptor
# Mt. Carmel
x2 = 432.424
y2 = 4250.202

m = (y2 - y1)/(x2 - x1)
c = (x2*y1 - x1*y2)/(x2 - x1)

# y = m*x + c

dy = 4252. - 4244.

print os.getcwd()

'''
fOut = open('vSlice.grd','w')
fOut.write('RE ELEVUNIT METERS\n')

z0 = 0.
for z in range(0,1010,10):
  for iy in range(101):
    y = 4244. + float(iy)*dy*0.01
    x = (y - c)/m
    fOut.write('   DISCCART  %8.1f %9.1f %6.2f %6.2f %6.2f\n'%(x*1.e3,y*1.e3,z0,z0,z))
fOut.close()

# Run AERMOD

shutil.copy('vSlice.inp','aermod.inp')
scipp_out = open('scipp.output','w')
h = subprocess.Popen(aermod,bufsize=0,shell=False,stdout=scipp_out,stderr=scipp_out)
h.communicate()
scipp_out.close()

# Cleanup
os.remove('aermod.inp')
if rmOut:
  os.remove('scipp.output')


#
# Horizontal Grid
#
dx = 0.2
dy = 0.2

# DOMAIN   425270.8 436695.8 4245320.0 4251178.0 2500.0
x0 = 425.
x1 = 437.
y0 = 4245.
y1 = 4252.
nx = int((x1 - x0)/dx) + 1
ny = int((y1 - y0)/dy) + 1
print nx,ny,nx*ny

z0 = 0.
fOut = open('hSlice.grd','w')
fOut.write('RE ELEVUNIT METERS\n')
for iy in range(ny):
  for ix in range(nx):
    fOut.write('   DISCCART  %8.1f %9.1f %6.2f  %6.2f\n'%((x0+float(ix)*dx)*1.e3,(y0+float(iy)*dy)*1.e3,z0,z0))
fOut.close()

hPost = 'hSlice.pst'
shutil.copy('hSlice.inp','aermod.inp')
scipp_out = open('scipp.output','w')
h = subprocess.Popen(aermod,bufsize=0,shell=False,stdout=scipp_out,stderr=scipp_out)
h.communicate()
scipp_out.close()

# Cleanup
os.remove('aermod.inp')
if rmOut:
  os.remove('scipp.output')

'''
# Set concentration/color Levels
isLinear = False
if isLinear:
    num    = 8
    vmin   = 0.0
    vmax   = 700.0
    levels = np.linspace(vmin,vmax,num=num)
    lnorm  = colors.Normalize(levels,clip=False)
else:
    num    = 7
    vmax   = 5  # int(np.log10(maxC)) + 1
    vmin   = -1 # vmax - num + 1
    levels = np.logspace(vmin,vmax,num=num,base=10.0)
    lnorm  = colors.LogNorm(levels,clip=False)
clrmap = plt.cm.get_cmap('jet',len(levels)-1)
print 'levels = ',levels

names = 'x y conc zelev  zhill zflag  ave grp date'.split()
print 'Names = ',names

#
vertDat = pd.read_table('vSlice.pst',skiprows=8,sep=r'\s*',header=0,names=names,dtype={'date':np.int64})
hrs     = vertDat['date'].unique()
vcMax   = vertDat['conc'].max()
print vertDat['conc'].min(),vcMax
print vertDat[vertDat['conc']==vcMax]

horzDat = pd.read_table('hSlice.pst',skiprows=8,sep=r'\s*',header=0,names=names,dtype={'date':np.int64})
hrs     = horzDat['date'].unique()
hcMax   = horzDat['conc'].max()
print horzDat['conc'].min(),hcMax
print horzDat[horzDat['conc']==hcMax]

for ihr,hr in enumerate(hrs):
  cZ = vertDat[vertDat['date']==hr]
  cH = horzDat[horzDat['date']==hr]
  print hr,cZ['conc'].max(),cH['conc'].max()

  if not isLinear:
    cZ['conc'][cZ['conc'] <= 0.] = 10.**(vmin-1)
    cH['conc'][cH['conc'] <= 0.] = 10.**(vmin-1)
  cZ['x'] = cZ['x']*1e-3
  cH['x'] = cH['x']*1e-3
  cH['y'] = cH['y']*1e-3
  
  # Vertical slice
  plt.clf()
  fig = plt.figure(1,frameon=False)
  axv = fig.add_subplot(1,2,1)
  plt.hold(True)

  triangles = tri.Triangulation(cZ['x'], cZ['zflag'])
  CS   = plt.tricontour(cZ['x'], cZ['zflag'], cZ['conc'], 15, norm = lnorm, levels=levels,linewidths=0.5, colors='k')
  if isLinear:
    CS = plt.tricontourf(cZ['x'], cZ['zflag'], cZ['conc'], 15, norm= lnorm, levels=levels, cmap=clrmap, vmin=vmin)
    CS.set_clim(vmin,vmax)
  else:
    CS = plt.tricontourf(cZ['x'],cZ['zflag'], cZ['conc'], 15, norm= lnorm, levels=levels, cmap=clrmap, vmin=10.**vmin)
    CS.set_clim(10.**vmin,10.**vmax)      
  CS.cmap.set_under('white') 
  plt.xlabel('Y(km)',fontsize=8)
  plt.ylabel('Z(m)',fontsize=8)
  plt.title('Conc (ug/m3) Vertical slice for time = %4.2f days'%(ihr/24.),fontsize=8)  
  plt.setp(axv.get_xticklabels(),fontsize=8)
  plt.setp(axv.get_yticklabels(),fontsize=8)

  # Horizontal Slice  
  axh = fig.add_subplot(1,2,2)
  triangles = tri.Triangulation(cH['x'], cH['y'])
  CS   = plt.tricontour(cH['x'], cH['y'], cH['conc'], 15, norm = lnorm, levels=levels,linewidths=0.5, colors='k')
  if isLinear:
    CS = plt.tricontourf(cH['x'], cH['y'], cH['conc'], 15, norm= lnorm, levels=levels, cmap=clrmap, vmin=vmin)
    CS.set_clim(vmin,vmax)
  else:
    CS = plt.tricontourf(cH['x'],cH['y'], cH['conc'], 15, norm= lnorm, levels=levels, cmap=clrmap, vmin=10.**vmin)
    CS.set_clim(10.**vmin,10.**vmax)      
  CS.cmap.set_under('white') 
   
  cbar = plt.colorbar(ticks=levels,format='%5.1e') # draw colorbar    
  plt.xlabel('X(km)',fontsize=8)
  plt.ylabel('Y(km)',fontsize=8)
  plt.title('Conc (ug/m3) Horizontal slice for time = %4.2f days'%(ihr/24.),fontsize=8)
  plt.setp(axh.get_xticklabels(),fontsize=8)
  plt.setp(axh.get_yticklabels(),fontsize=8)
  
  plt.hold(False)
  plt.savefig('vSlice_%04d.png'%ihr)
  
  if ihr > 10:
    break
  
print 'Done'
  

#!/bin/env python
import os
import sys
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import sqlite3
import time
import subprocess
sys.path.append('/home/user/bnc/python')
import smp2db
import setSCIparams as SCI

def mainProg(obsDb,prjName,pltFname,cFactor=1.,tFactor=1.,cCut = 1.e-4,fltDb=None):

  print 'Plotting concentration time series for ',obsDb,prjName,' as ',pltFname 
  preDb = '%s.smp.db'%prjName

  # Observed data
  obsConn = sqlite3.connect(obsDb)
  obsConn.row_factory = sqlite3.Row
  obsCur = obsConn.cursor()

  # Predicted data
  preConn = sqlite3.connect(preDb)
  preConn.row_factory = sqlite3.Row
  preCur = preConn.cursor()

  if fltDb:
    # Filtered data
    fltConn = sqlite3.connect(fltDb)
    fltConn.row_factory = sqlite3.Row
    fltCur = fltConn.cursor()

  # Observed station locations 
  obsXy = smp2db.db2Array(obsCur,'SELECT distinct xstn,ystn from obsTable where \
                             conc >= 0. order by xstn,ystn')
  print 'minmax x,y = ',min(obsXy[:,0]),max(obsXy[:,0]),min(obsXy[:,1]),max(obsXy[:,1])

  # Observed concentrations with conc >=0.
  obsConc = smp2db.db2Array(obsCur,'SELECT xStn,yStn,EpTime,conc from obsTable where \
                             conc >= 0. order by xStn,yStn,EpTime')
  cOmax = max(obsConc[:,3])
  print 'Max Obs Conc = ',cOmax
  
  # Predicted concentrations 
  preConc = smp2db.db2Array(preCur,'SELECT a.xSmp,a.ySmp,p.EpTime,p.value from smpTable p,samtable a where \
                       p.colno=a.colno and a.varname="C" order by a.xSmp,a.ySmp,p.EpTime')
  cPmax = max(preConc[:,3])*cFactor
  print 'Max Pre Conc = ',cPmax
  cMax = max(cOmax,cPmax)
  cCut = cCut*cMax

  # Get time for start of Reverse run
  mySCIpattern = SCI.Pattern()
  mySciFiles   = SCI.Files(prjName,mySCIpattern)
  (nmlNames,nmlValues) = mySCIpattern.readNml(mySciFiles.inpFile)
  i = nmlNames.index('time2')
  totEndHr = float(nmlValues[i]['tend_hr'])
  print '\nProject tend_hr = ',totEndHr
  if totEndHr < 5/60.:
    timeLimit = totEndHr*3600.
    timeLabel = 'Time(sec)' 
    timeFactor = 1.
  elif totEndHr < 5.:
    timeLimit = totEndHr*60.
    timeLabel = 'Time(min)' 
    timeFactor = 1./60.
  else:
    timeLimit = totEndHr
    timeLabel = 'Time(hr)' 
    timeFactor = 1./3600.
  if cFactor == 1.:
    yLabel = 'Conc(kg/m3)'
  elif cFactor == 1.e-9:
    yLabel = 'Conc(ng/m3)'
  else:
    yLabel = 'Conc'


  i = nmlNames.index('domain')
  xmin = float(nmlValues[i]['xmin'])
  xmax = float(nmlValues[i]['xmax'])
  ymin = float(nmlValues[i]['ymin'])
  ymax = float(nmlValues[i]['ymax'])
  dy   = ymax - ymin
  dyl  = dy/100.
  cmap = nmlValues[i]['cmap']

  #
  (nmlNames,nmlValues) = mySCIpattern.readNml(mySciFiles.scnFile)
  i = nmlNames.index('scn')
  xrel = float(nmlValues[i]['xrel'])
  yrel = float(nmlValues[i]['yrel'])

  # Adjust the minimum time and the time units
  minEpTime = min(min(preConc[:,2]),min(obsConc[:,2]))
  print 'minEpTime = ',minEpTime
  print 'MinMax %s = %8.3f %8.3f'%(timeLabel,(min(preConc[:,2])-minEpTime)*timeFactor,(max(preConc[:,2])-minEpTime)*timeFactor)
  print 'MinMax Conc limits = %13.5e %13.5e %s'%(cCut,cMax,yLabel)
  preConc[:,2] = (preConc[:,2] - minEpTime)*timeFactor
  obsConc[:,2] = (obsConc[:,2] - minEpTime)*timeFactor

  fList = []
  # Set up plot parametes
  params1 = {'axes.labelsize': 10, 'text.fontsize': 10, 'xtick.labelsize': 10,
              'ytick.labelsize': 10, 'legend.pad': 0.1,  
              'legend.fontsize': 8, 'lines.markersize': 5, 'lines.width': 2.0,
              'font.size': 10, 'text.usetex': False}

  plt.rcParams.update(params1)
  # Plot station locations
  ifig = 1
  fig = plt.figure(ifig)
  plt.clf()
  fig.hold(True)
  fName = 'StationXY.pdf'
  fList.append(fName)
  plt.scatter(obsXy[:,0],obsXy[:,1])
  plt.title('Station locations')
  cmap = cmap.lower().replace("'","").strip()
  print 'cmap = "',cmap,'"'
  if cmap == 'latlon':
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
  elif cmap == 'cartesian':
    plt.xlabel('X(km)')
    plt.ylabel('Y(km)')
  else:
    plt.xlabel('X(m)')
    plt.ylabel('Y(m)')
  for ip,xy in enumerate(obsXy):
    plt.text(xy[0],xy[1]+dyl,'%d'%(ip+1),fontsize=7)
  # plot source location from pre file
  plt.scatter([xrel,],[yrel,],color='r',marker='d')
  plt.text(xrel,yrel+dyl,'S',fontsize=7)
  # set domain limits
  plt.xlim(xmin,xmax)
  plt.ylim(ymin,ymax)
  fig.hold(False)
  plt.savefig(fName)

  # For each station plot Co and Cp time series
  nPts  = 30
  isub  = 0
  minDx = 0.01
  for ip,xy in enumerate(obsXy):
    Co = []
    Cf = np.array([])
    for cobs in obsConc:
      if cobs[0] < xy[0] - minDx:
        continue
      if abs(xy[0]-cobs[0])+abs(xy[1]-cobs[1]) < minDx:
        Co.append((cobs[2],cobs[3]))
        if fltDb and not Cf.any():
          selectStr = 'SELECT epTime,cSen from senTable where xSen = %g and ySen = %g order by epTime'%(cobs[0],cobs[1])
          Cf = smp2db.db2Array(fltCur,selectStr)
          print selectStr, len(Cf)
          if len(Cf) > 0:
            Cf[:,0] = (Cf[:,0] - minEpTime + 1)*timeFactor
      if cobs[0] > xy[0] + minDx:
        break
    Co = np.array(Co,dtype=float)
                                            
    Cp = [] 
    for cpre in preConc:
      if cpre[0] < xy[0] - minDx:
        continue
      if abs(xy[0]-cpre[0])+abs(xy[1]-cpre[1]) < minDx:
        Cp.append((cpre[2]/tFactor,cpre[3]*cFactor))
      if cpre[0] > xy[0] + minDx:
        break
    Cp  = np.array(Cp,dtype=float)
    Cpm = ma.masked_where(Cp[:,1]==0.,Cp[:,1])
    print 'ip,xy  = ',ip,xy
    print 'Cp = ',Cp[:,0],Cpm
    if max(Co[:,1]) + max(Cp[:,1]) > 0.:
      Co[:,1] = Co[:,1] + cCut
      if len(Cf) > 0:
        Cf[:,1] = Cf[:,1]*cFactor + cCut
      Cpm = Cpm + cCut
      if isub%9 == 0:
        ifig += 1
        isub = 0
        fig = plt.figure(ifig)
        plt.clf()
        fName = 'tSeries%03d.pdf'%ifig
        fig.subplots_adjust(bottom=0.12)
        fig.suptitle('Time series of observed and predicted concentration', fontsize=10, fontweight='bold')
        fig.hold(True)
        LglHdl = []
        LglLbl = []
      isub += 1
      subno = 330 + isub
      print 'Figure, subplot = ',ifig,isub
      ax = fig.add_subplot(subno)
      if max(Co[:,1]) >= cCut:
        xData = Co[:,0] 
        yData = Co[:,1] 
        print 'Co = ',xData,yData
        ratio = max(1,int(xData.size/nPts)+1)
        xData = xData[::ratio]
        yData = yData[::ratio]
        print 'Downsampled Co = ',xData,yData
        Lh = ax.semilogy(xData,yData,'g*')
        if 'Observed' not in LglLbl: 
          LglHdl.append(Lh)
          LglLbl.append('Observed')
        if len(Cf) > 0:
          xData = Cf[:,0]
          yData = Cf[:,1]
          print 'Cf = ',xData,yData
          Lh = ax.semilogy(xData,yData,marker='s',linestyle='None',markerfacecolor='None',markeredgecolor='red')
          if 'Filtered' not in LglLbl: 
            LglHdl.append(Lh)
            LglLbl.append('Filtered')
      if max(Cp[:,1]) > 0.:
        ratio = max(1,int(Cp[:,0].size/nPts)+1)
        xData = Cp[:,0][::ratio]
        yData = Cpm[::ratio]
        Lh = ax.semilogy(xData,yData,'bo',markersize=3)
        if 'Predicted' not in LglLbl: 
          LglHdl.append(Lh)
          LglLbl.append('Predicted')
      #if isub > 6:
        ax.set_xlabel(timeLabel,fontsize=9)
        plt.setp(ax.get_xticklabels(),fontsize=8)
      #else:
      #  ax.set_xticklabels([])
      #if isub%3 == 1:
        ax.set_ylabel(yLabel,fontsize=9)
        plt.setp(ax.get_yticklabels(),fontsize=8)
      #else:
      #  ax.set_yticklabels([])
      ax.text(.4,0.85,'%d(%6.2f,%6.2f)'%(ip+1,xy[0],xy[1]),transform=ax.transAxes,fontsize=8)
      ax.set_xlim(0,timeLimit)
      ax.set_ylim(cCut/3.33,cMax*3.33)
      if isub%9 == 0:
        axl = plt.axes([0.61,0.04,0.3,0.01],frameon=False)   # Concentration type
        axl.xaxis.set_visible(False)
        axl.yaxis.set_visible(False)
        axl.legend((LglHdl),(LglLbl),ncol=3)
        fig.hold(False)
        plt.savefig(fName)
        fList.append(fName)
        print 'Created ',fName,'\n'
      print 'Max Co,Cp  = ',max(Co[:,1]),max(Cp[:,1]),'\n'

  if fName not in fList:
    fig.hold(False)
    plt.savefig(fName)
    fList.append(fName)
    print 'Created ',fName,'\n'

  Popen = subprocess.Popen
  PIPE  = subprocess.PIPE

  command = ["gs","-dBATCH","-dNOPAUSE","-q","-sDEVICE=pdfwrite","-sOutputFile=%s"%pltFname]
  command.extend(fList)
  (output, errmsg) = Popen(command,stdout=PIPE,stderr=PIPE).communicate()
  print 'Joined all pdf file to create ',pltFname,'\n'

  command = ["rm","-f"]
  command.extend(fList)
  (output, errmsg) = Popen(command,stdout=PIPE,stderr=PIPE).communicate()

  obsConn.close()
  preConn.close()
  if fltDb:
    fltConn.close()
    
# Main program
if __name__ == '__main__':
  obsDb = 'Case001Obs.db'
  prjName = 'FwdCase001'
  fltDb = 'RevCase001_10_Filtered.sen.db'
  pltFname = 'Case001_10_TimeSeries.pdf'
  cFactor = 1.    # kg/m3 to kg/m3
  cCut = 1e-4
  mainProg(obsDb,prjName,pltFname,cFactor=cFactor,cCut=cCut,fltDb=fltDb)

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
import PlotSampler
import smp2db
import pltRevMassEstimate 

def mainProg(obsDbName,prjName,pltFname,relParam=None,cFactor=1.,fltDbName=None,estParam=None):

  sourceLoc = [[],[]]

  if relParam:
    actualRel = 0
    sourceLoc[actualRel] = relParam.srcLoc
    preDb = '%s.smp.db'%prjName
  else:
    actualRel = -1

  if estParam:
    estRel = actualRel + 1
    sourceLoc[estRel] = [estParam.relX,estParam.relY]
  else:
    estRel = -1
  
  # Observed data
  obsConn = sqlite3.connect(obsDbName)
  obsConn.row_factory = sqlite3.Row
  obsCur = obsConn.cursor()

  # Predicted data
  preConn = sqlite3.connect(preDb)
  preConn.row_factory = sqlite3.Row
  preCur = preConn.cursor()

  # Filtered data
  if fltDbName:
    fltConn = sqlite3.connect(fltDbName)
    fltConn.row_factory = sqlite3.Row
    fltCur = fltConn.cursor()

  # Observed station locations 
  obsXy = smp2db.db2Array(obsCur,'SELECT distinct xstn,ystn from obsTable where \
                             conc >= 0. order by xstn,ystn')
  print 'minmax x,y = ',min(obsXy[:,0]),max(obsXy[:,0]),min(obsXy[:,1]),max(obsXy[:,1])

  # Create temporary table of observed concentrations conc >=0.
  obsCur.execute('CREATE temp table vObsTable as SELECT xStn,yStn,epTime,conc from obsTable \
                  where conc >= 0. order by xStn,yStn,epTime')
  obsMax = smp2db.db2Array(obsCur,'select max(conc) from vObsTable')[0][0]
  print 'Max obs conc = ',obsMax
  
  # Create temporary table of predicted concentrations 
  preCur.execute('CREATE temp table vPreTable as SELECT a.xSmp,a.ySmp,p.epTime,p.value from \
                  smpTable p,samtable a where p.colno=a.colno and a.varname="C" order by \
                  a.xSmp,a.ySmp,p.epTime')
  predMax = smp2db.db2Array(preCur,'select max(value) from vPreTable')[0][0]*cFactor
  print 'Max pre conc = ',predMax

  clrMax = int(np.log10(max(obsMax,predMax)/obsMax)) + 1
  clrMin = clrMax - 7
  clrLev = clrMax - clrMin + 1
  pltsmp = PlotSampler.Plots(clrLev=clrLev,clrMin=clrMin,clrMax=clrMax,logScale=True,fext='.pdf')

  cCut = obsMax*1.e-6

  clrMin = 10.**clrMin
  clrMax = 10.**clrMax
  xMin  = min(obsXy[:,0])
  xMax  = max(obsXy[:,0])
  if actualRel > 0 : 
    xMin  = min(xMin,sourceLoc[actualRel][0])
    xMax  = max(xMax,sourceLoc[actualRel][0])
  if estRel > 0 : 
    xMin  = min(xMin,sourceLoc[estRel][0])
    xMax  = max(xMax,sourceLoc[estRel][0])
  dx    = (xMax-xMin)*0.1
  xMin  = xMin - dx
  xMax  = xMax + dx
  dxl   = dx*0.1

  yMin  = min(obsXy[:,1])
  yMax  = max(obsXy[:,1])
  if relParam: 
    yMin  = min(yMin,sourceLoc[actualRel][1])
    yMax  = max(yMax,sourceLoc[actualRel][1])
  if estParam: 
    yMin  = min(yMin,sourceLoc[estRel][1])
    yMax  = max(yMax,sourceLoc[estRel][1])
  dy    = (yMax-yMin)*0.1
  yMin  = yMin - dy
  dyl   = dy*0.1
  yMax  = yMax + dy

  cMax = []
  for ip,xy in enumerate(obsXy):
   
    # Max from observations
    obsCur.execute('SELECT max(conc) from vObsTable where xStn = ? and yStn = ?',(xy[0],xy[1]))
    cox = obsCur.fetchone()
    #print '\nX,Y = ',xy[0],xy[1]
    try: 
      cox = float(cox[0])
    except TypeError:
      cox = -999.

    # Max from prediction
    preCur.execute('SELECT max(value) from vPreTable where xSmp = ? and ySmp = ?',(xy[0],xy[1]))
    cpx = preCur.fetchone()
    try: 
      cpx = float(cpx[0])
    except TypeError:
      cpx = -999.

    # Max from filtered data
    if fltDbName:
      fltCur.execute('SELECT max(cSen) from senTable where xSen = ? and ySen = ?',(xy[0],xy[1]))
      cfx = fltCur.fetchone()
      try: 
        cfx = float(cfx[0])
      except TypeError:
        cfx = -999.
    else: 
      cfx = -999.

    cMax.append([cox,cpx,cfx])
    print 'x,y,cOmax,cPmax,cFmax = ',xy[0],xy[1],cox,cpx,cfx

  cMax = np.array(cMax,dtype=float)
  cMax[:,1:3] = cMax[:,1:3]*cFactor
  cMax[:,0:3] = cMax[:,0:3]/obsMax
  cMax_masked = ma.masked_less(cMax,0.,copy=True) + cCut*0.1
  mask = ma.getmask(cMax_masked[:,2])
  xF = ma.array(obsXy[:,0],copy=True,mask=mask)
  yF = ma.array(obsXy[:,1],copy=True,mask=mask)

  # Dummy plot for getting colorbar scale
  print 'clr,x,y MinMax = ',clrMin, clrMax, xMin, xMax, yMin, yMax
  cset = plt.scatter([xMin,xMax],[yMin,yMax],c=[clrMin,clrMax],\
                    vmin=pltsmp.vmin,vmax=pltsmp.vmax,norm=pltsmp.lnorm,cmap=pltsmp.clrMap)
  # Plot 2d concentraion
  obsTimeArray = smp2db.db2Array(obsCur,"select distinct epTime from vObsTable order by epTime")
  preTimeArray = smp2db.db2Array(preCur,"select distinct epTime from vPreTable order by epTime")
  dtPre = min(np.diff(preTimeArray[:,0]))
  dtObs = min(np.diff(obsTimeArray[:,0]))
  minEpTime = max(obsTimeArray[0],preTimeArray[0])
  maxEpTime = min(obsTimeArray[-1],preTimeArray[-1])
  maxDt = max(dtPre,dtObs)
  dtDiff= maxDt/2.
  print 'maxDiffTime = ',maxDt,dtPre,dtObs
  
  ifig = 0
  fList = []
  for tSec in np.arange(minEpTime,maxEpTime+maxDt,maxDt):
    # Plot station locations with max concentration
    ifig += 1
    print 'IFIG at time(sec) = ',ifig,tSec
    fig = plt.figure(ifig)
    plt.clf()
    fig.subplots_adjust(right=0.8)
    fig.hold(True)
    fName = 'Fig2d_%02d.pdf'%ifig
    if ifig == 1:
      scaleStr = 'scaled by ' + ('%13.2e'%obsMax).strip()
      fig.suptitle('Max concentrations %s'%scaleStr,fontsize=11,fontweight='bold')
      xO = xP = obsXy[:,0]
      yO = yP = obsXy[:,1]
      cO = cMax_masked[:,0]
      cP = cMax_masked[:,1]
      cF = cMax_masked[:,2]
    else:
      fig.suptitle('Concentrations %s at time %6.2f'%(scaleStr,tSec-minEpTime),\
                    fontsize=11,fontweight='bold')
      # get observed concentration
       
      #print 'ObsTimes = ',smp2db.db2Array(obsCur,"select distinct(eptime) from vObsTable where \
      #                                            epTime between %15.2f and %15.2f"%(tSec-dtDiff,tSec+dtDiff))
      obsArray = smp2db.db2Array(obsCur,"select xStn,yStn,avg(conc) from vObsTable where  \
                                         epTime between %15.2f and %15.2f group by xStn,yStn"%(tSec-dtDiff,tSec+dtDiff))
      cO = np.array([]) 
      if len(obsArray) > 0:
        cOb = obsArray[:,2]
        if max(cOb) > 0:
          xO = obsArray[:,0]
          yO = obsArray[:,1]
          cO = cOb/obsMax
      # get filtered concentration
      if fltDbName:
        #print 'fltTimes = ',smp2db.db2Array(fltCur,"select distinct(eptime) from senTable where \
        #                                            epTime between %15.2f and %15.2f"%(tSec-dtDiff,tSec+dtDiff))
        fltArray = smp2db.db2Array(fltCur,"select xSen,ySen,avg(cSen) from senTable where \
                                           epTime between %15.2f and %15.2f group by xSen,ySen"%(tSec-dtDiff,tSec+dtDiff))
        if len(fltArray) > 0:
          xF = fltArray[:,0]
          yF = fltArray[:,1]
          cF = fltArray[:,2]/obsMax
        else:
          cF = np.array([]) 
      else:
        cF = np.array([]) 
      # get predicted concentration
      #print 'preTimes = ',smp2db.db2Array(preCur,"select distinct(eptime) from vPreTable where \
      #                                            epTime between %15.2f and %15.2f"%(tSec-dtDiff,tSec+dtDiff))
      calArray = smp2db.db2Array(preCur,"select xSmp,ySmp,avg(value) from vPreTable where \
                                         epTime between %15.2f and %15.2f group by xSmp,ySmp"%(tSec-dtDiff,tSec+dtDiff))
      if len(calArray) > 0:
        xP = calArray[:,0]
        yP = calArray[:,1]
        cP = calArray[:,2]*cFactor/obsMax
      else:
        cP = np.array([]) 

    print 'Scaled cO = ',cO
    print 'Scaled cF = ',cF 
    print 'Scaled cP = ',cP 

    #-- Subplot 1

    # Observation sampler concentrations
    ax = fig.add_subplot(2,1,1)
    if len(cO) > 0:
      ax.scatter(xO,yO,s=10,c=cO,vmin=pltsmp.vmin,vmax=pltsmp.vmax,norm=pltsmp.lnorm,cmap=pltsmp.clrMap)
    if len(cF) > 0:
      ax.plot(xF,yF,marker='s',linestyle='None',markersize=5,markerfacecolor='None',markeredgecolor='red')

    # Add id and filter symbols
    for ip,xy in enumerate(obsXy):
      # Add sampler id
      ax.text(xy[0],xy[1]+dyl,'%d'%(ip+1),fontsize=6)
      if (xy[0],xy[1]) not in zip(xO,yO):
        ax.plot(xy[0],xy[1],marker='o',linestyle='None',markersize=3,
                markerfacecolor='None',markeredgecolor='black')
  
    # Add actual and estimated source locations
    addSrcLoc(ax,actualRel,estRel,sourceLoc)

    # set labels and limits
    ax.set_ylabel('y(Km)')
    ax.set_xlim([xMin,xMax])
    ax.set_ylim([yMin,yMax])
    
    #-- Subplot 2

    # Predicted sampler concentrations
    ax = fig.add_subplot(2,1,2)
    ax.scatter(xP,yP,s=10,c=cP,vmin=pltsmp.vmin,vmax=pltsmp.vmax,norm=pltsmp.lnorm,cmap=pltsmp.clrMap)
    if len(cF) > 0:
      ax.plot(xF,yF,marker='s',linestyle='None',markersize=5,markerfacecolor='None',markeredgecolor='red')

    # Add sampler id
    for ip,xy in enumerate(obsXy):
      ax.text(xy[0],xy[1]+dyl,'%d'%(ip+1),fontsize=6)
      if (xy[0],xy[1]) not in zip(xP,yP):
        ax.plot(xy[0],xy[1],marker='o',linestyle='None',markersize=3,\
                markerfacecolor='None',markeredgecolor='black')

    # Add actual and estimated source locations
    addSrcLoc(ax,actualRel,estRel,sourceLoc)

    # set labels and limits
    ax.set_xlabel('x(km)')
    ax.set_ylabel('y(km)')
    ax.set_xlim([xMin,xMax])
    ax.set_ylim([yMin,yMax])

    #-- Set color bar for the plot
    cax = plt.axes([0.85,0.1,0.03,0.8])
    plt.colorbar(cset,cax=cax)
    fig.hold(False)
    plt.savefig(fName)
    fList.append(fName)
    print 'Created plot ',fName
  PlotSampler.joinPDF(fList,pltFname)
  obsConn.close()
  preConn.close()
  if fltDbName:
    fltConn.close()

def addSrcLoc(ax,actualRel,estRel,sourceLoc):

    if actualRel >= 0 :
      # Actual Source Location
      ax.plot(sourceLoc[actualRel][0],sourceLoc[actualRel][1],marker='d',linestyle='None',markersize=4,\
              markerfacecolor='Green',markeredgecolor='black')
      ax.text(sourceLoc[actualRel][0],sourceLoc[actualRel][1],'S',fontsize=7)
      print 'Add actual src location ',sourceLoc[actualRel][0],sourceLoc[actualRel][1]

    if estRel >= 0:
      # Estimated Source Location
      ax.plot(sourceLoc[estRel][0],sourceLoc[estRel][1],marker='*',linestyle='None',markersize=4,\
              markerfacecolor='Indigo',markeredgecolor='black')
#             markerfacecolor=r'#00FFFF'
      ax.text(sourceLoc[estRel][0],sourceLoc[estRel][1],'E',fontsize=7)
      print 'Add est. src location ',sourceLoc[estRel][0],sourceLoc[estRel][1]
    
# Main program
if __name__ == '__main__':
  obsDbName = 'Case044Obs.db'
  prjName = 'FwdCase044'
  nFlt    = 10
  fltDbName = 'RevCase044_10_Filtered.sen.db'
  massList = [[0.0, 0.0094374999999999997], [0.16666666666666666*3600., 0.0094374999999999997]]  # (hr kg[/s])
  myRel = pltRevMassEstimate.relClass('20070921105000',massList)
  myRel.addLoc([1.695, 0.912])
  cFactor   = 1.    # kg/m3 to kg/m3
  mainProg(obsDbName, prjName, 'Case044_2dSeries%d.pdf'%nFlt, relParam=myRel,\
           cFactor=cFactor, fltDbName=fltDbName)

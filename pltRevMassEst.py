#!/usr/bin/python
import os
import sys
import fileinput
import sqlite3
import subprocess
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
sys.path.append('/home/user/bnc/python')
import setSCIparams as SCI
import smp2db


class relClass:
  def __init__(self,startTimeString,massList):
    self.startTimeString = startTimeString
    self.massList = massList 
  def addLoc(self,srcLoc):
    self.srcLoc = srcLoc

def mainProg(obsDbName,prjName,pltFile,myRel,cFactor=1.):

  # Observed data
  obsConn = sqlite3.connect(obsDbName)
  obsConn.row_factory = sqlite3.Row
  obsCur = obsConn.cursor()

  # Filtered data
  fltConn = sqlite3.connect('%s_Filtered.sen.db'%prjName)
  fltConn.row_factory = sqlite3.Row
  fltCur = fltConn.cursor()

  # Reverse smp data
  preConn = sqlite3.connect('%s.smp.db'%prjName)
  preConn.row_factory = sqlite3.Row
  preCur = preConn.cursor()

# Get time for start of Reverse run
  mySCIpattern = SCI.Pattern()
  mySciFiles   = SCI.Files(prjName,mySCIpattern)
  (nmlNames,nmlValues) = mySCIpattern.readNml(mySciFiles.inpFile)
  i = nmlNames.index('time1')
  startRevYr = float(nmlValues[i]['year_start'])
  startRevMo = float(nmlValues[i]['month_start'])
  startRevDay = float(nmlValues[i]['day_start'])
  startRevHr = float(nmlValues[i]['tstart'])
  revStartEpTime = smp2db.getEpTime(startRevYr,startRevMo,startRevDay,startRevHr)
  i = nmlNames.index('time2')
  revEndHr = float(nmlValues[i]['tend_hr'])
  revEndEpTime = revStartEpTime - revEndHr*3600.
  print 'revStartEpTime, revEndEpTime = ',revStartEpTime,revEndEpTime
  print '\nSampler start day and time for reverse project = ',startRevDay,startRevHr

  startEpTime = smp2db.getEpTime(myRel.startTimeString)
  minEpTime = min(startEpTime,revEndEpTime)
  runSec = revStartEpTime - minEpTime
  print '\nProject run time(Secs) = ',runSec

  if runSec < 300.:
    timeLabel = 'Time(sec)' 
    timeFactor = 1.
  elif runSec < 1800.:
    timeLabel = 'Time(min)' 
    timeFactor = 1./60.
  else:
    timeLabel = 'Time(hr)' 
    timeFactor = 1./3600.
  timeLimit = runSec*timeFactor
  print timeLimit, timeLabel

  if cFactor == 1.:
    yLabel = 'Conc(kg/m3)'
  elif cFactor == 1.e-9:
    yLabel = 'Conc(ng/m3)'
  else:
    yLabel = 'Conc'
  mySCIpattern = SCI.Pattern()
  mySciFiles   = SCI.Files(prjName,mySCIpattern)
  (nmlNames,nmlValues) = mySCIpattern.readNml(mySciFiles.inpFile)
  i = nmlNames.index('domain')
  xmin = float(nmlValues[i]['xmin'])
  xmax = float(nmlValues[i]['xmax'])
  ymin = float(nmlValues[i]['ymin'])
  ymax = float(nmlValues[i]['ymax'])
  dy   = ymax - ymin
  dyl  = dy/100.
  cmap = nmlValues[i]['cmap']

  actualMass = np.zeros([len(myRel.massList), 2])
  for i,aMass in enumerate(actualMass):
    aMass[0] = myRel.massList[i][0]*timeFactor
    aMass[1] = myRel.massList[i][1]
  srcMassMin = min(actualMass[:,1])*1e-2
  srcMassMax = max(actualMass[:,1])*1e4
  print 'actualMass = ',actualMass

  obsXy = smp2db.db2Array(obsCur,'SELECT distinct xstn,ystn from obsTable where \
                                  conc >= 0. order by xstn,ystn')

  # Set up plot parameters
  params1 = {'axes.labelsize': 10, 'text.fontsize': 10, 'xtick.labelsize': 10,
                'ytick.labelsize': 10, 'legend.pad': 0.1,  
                'legend.fontsize': 8, 'lines.markersize': 6, 'lines.width': 2.0,
                'font.size': 10, 'text.usetex': False}
  plt.rcParams.update(params1)

  ifig = 0
  fList = []
  isub = 0
  for ip,xy in enumerate(obsXy):
    selectStr = 'SELECT epTime,cSen,matName,matType from senTable where xSen = %g and ySen = %g order by epTime'%(xy[0],xy[1])
    fltCur.execute(selectStr)
    rows = fltCur.fetchall()
    if len(rows) > 0:
      # loop for each material
      for row in rows:
        (epTime,cSen,matName,matType)  = (float(row[0]),float(row[1]),row[2],row[3])
        # only hit as of now
        if matType != 'N':
          selectStr = 'SELECT p.epTime,p.value from smptable p, samtable a where p.colno=a.colno \
                       and a.matName="%s" and a.varName ="C" order by p.epTime'%matName
          cRev = smp2db.db2Array(preCur,selectStr)
          # Adjust to time relative to start epTime
          print cRev[:,0]
          cRev[:,0] = (cRev[:,0] - minEpTime)*timeFactor
          print 'cRev = '
          print cRev[:,0]
          print cRev[:,1]
          cMasked = ma.masked_where(cRev[:,1]==0.,1./cRev[:,1])
          print 'ip, xy = ',ip+1,xy[0],xy[1],epTime,cSen,matName,matType 
          if max(cRev[:,1]) > 0.:
            if isub%9 == 0:
              ifig += 1
              isub = 0
              fig = plt.figure(ifig)
              plt.clf()
              fName = 'Rev%d.pdf'%ifig
              fig.subplots_adjust(bottom=0.12)
              fig.suptitle('Predicted mass for actual source location and duration', fontsize=10, fontweight='bold')
              fig.hold(True)
              LglHdl = []
              LglLbl = []
            isub += 1
            subno = 330 + isub
            print 'Figure, subplot = ',ifig,isub
            ax = fig.add_subplot(subno)
            # All times are relative to minEpTime 
            # plot the predicted mass at source location
            Lh = ax.semilogy(cRev[:,0],cMasked)
            if 'Predicted release mass' not in LglLbl:
              LglHdl.append(Lh)
              LglLbl.append('Predicted release mass')
            # plot actual mass release
            Lh = ax.semilogy(actualMass[:,0],actualMass[:,1])
            if 'Actual release mass' not in LglLbl:
              LglHdl.append(Lh)
              LglLbl.append('Actual release mass')
            # plot reverse material release time. Release mass not used currently
            print 'reverse release time ',(epTime-minEpTime)*timeFactor,actualMass[0,1]
            Lh = ax.semilogy((epTime-minEpTime)*timeFactor,actualMass[0,1],marker='d')
            if 'Reverse release time' not in LglLbl:
              LglHdl.append(Lh)
              LglLbl.append('Reverse release time')
            if isub > 6:
              ax.set_xlabel(timeLabel,fontsize=9)
              plt.setp(ax.get_xticklabels(),fontsize=8)
            else:
              ax.set_xticklabels([])
            if isub%3 == 1:
              ax.set_ylabel('Mass(kg)',fontsize=9)
              plt.setp(ax.get_yticklabels(),fontsize=8)
            else:
              ax.set_yticklabels([])
            ax.text(.5,0.85,'%s,%7.2f%s'%(matName,(epTime-minEpTime)*timeFactor,timeLabel.replace('Time','')),\
                    transform=ax.transAxes,fontsize=7)
            ax.text(.5,0.77,'%d(%6.2f,%6.2f)'%(ip+1,xy[0],xy[1]),transform=ax.transAxes,fontsize=7)
            ax.set_xlim([0,timeLimit*1.1])
            ax.set_ylim([srcMassMin,srcMassMax])
            if isub%9 == 0:
              axl = plt.axes([0.61,0.04,0.3,0.01],frameon=False)   # Concentration type
              axl.xaxis.set_visible(False)
              axl.yaxis.set_visible(False)
              print LglHdl
              print LglLbl
              axl.legend((LglHdl),(LglLbl),ncol=3)
              fig.hold(False)
              plt.savefig(fName)
              fList.append(fName)
              print 'Created ',fName,'\n'

  if fName not in fList:
    fig.hold(False)
    plt.savefig(fName)
    fList.append(fName)
    print 'Created ',fName,'\n'

  Popen = subprocess.Popen
  PIPE  = subprocess.PIPE

  command = ["gs","-dBATCH","-dNOPAUSE","-q","-sDEVICE=pdfwrite","-sOutputFile=%s"%pltFile]
  command.extend(fList)
  (output, errmsg) = Popen(command,stdout=PIPE,stderr=PIPE).communicate()
  print 'Joined pdf to create ',pltFile,'\n'

  command = ["rm","-f"]
  command.extend(fList)
  (output, errmsg) = Popen(command,stdout=PIPE,stderr=PIPE).communicate()

  obsConn.close()
  preConn.close()
  fltConn.close()

if __name__ == '__main__':
  nFlt = 10
  obsDbName = 'Case044Obs.db'
  revPrjName = 'RevCase044_%d'%nFlt
  massList = [[0.0, 0.0094374999999999997], [0.16666666666666666*3600., 0.0094374999999999997]]  # (hr kg[/s])
  myRel = relClass('20070921110500',massList)
  mainProg(obsDbName,revPrjName,'Case044_10_RevMassEstimate.pdf',myRel)

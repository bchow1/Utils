import os
import sys
import shutil
import re
import optparse
import fileinput
import subprocess
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
import getSmpStats
import run_cmd

# Original file from /home/user/bnc/TestHPAC/Outputs/100810.0944/Experimental/DTRAPhaseI

# Reads the experimental data from cmens-01.dat, cvars-01.dat etc. files 
# and calculates the cmax,sigmac/C,sigy,sigt,dmax and sigmad/D

# Also calls getSmpStats.py to get the same statistics from the
# SCIPUFF smp files and plots the results.

def getStat(cmeanFile,cvarFile):    
  # Read cmeanFile
  for line in fileinput.input( cmeanFile ):
    if fileinput.isfirstline():
      smpHead = line 
    elif fileinput.lineno() == 2:
      nx = int(line.strip())
    else:
      ySmp = np.array(map(float,line.split()),dtype=float)
      break
  fileinput.close()
  #print smpHead.rstrip()
  # Read cvarFile
  for line in fileinput.input( cvarFile ):
    if fileinput.isfirstline():
      smpHead = line 
    elif fileinput.lineno() == 2:
      nSmp = int(line.strip())
    else:
      xsmp = np.array(map(float,line.split()),dtype=float)
      break
  fileinput.close()
  #
  nSkipRows = 3
  cScale = 1.
  cmData = np.loadtxt(cmeanFile,skiprows=nSkipRows)
  cvData = np.loadtxt(cvarFile,skiprows=nSkipRows)
  dmeanFile = cmeanFile.replace('cmens','dmens')
  dvarFile  = cvarFile.replace('cvars','dvars')
  dmData = np.loadtxt(dmeanFile,skiprows=nSkipRows)
  dvData = np.loadtxt(dvarFile,skiprows=nSkipRows)
  tcol = cmData[:,0]
  if max(cvData[:,0] - tcol) > 0. :
    print 'Error: Time do not match'
    print cvData[:,0] - tcol
    sys.exit()

  dtcol = np.diff(tcol)
  nt = len(tcol)
  #print 'nt,nsmp = ',nt,nSmp
  cmean = np.zeros((nt,nSmp),float)
  cvar  = np.zeros((nt,nSmp),float)
  dmean = np.zeros(nSmp,float)
  dvar  = np.zeros(nSmp,float)
  for i in range(nSmp):
    cmean[:,i] = cmData[:,i+1]*cScale
    cvar[:,i]  = cvData[:,i+1]*cScale*cScale
    dmean[:,i] = dmData[:,i+1]*cScale
    dvar[:,i]  = dvData[:,i+1]*cScale*cScale
  cmax = np.zeros((nt),float)
  dmax  = 0.
  idmax = 0
  for i in range(nSmp):
    if dmean[i] > dmax:
      dmax  = dmean[i]
      idmax = i
    #print dmean[i],dvar[i]
  #print idmax, dmean[idmax], dvar[idmax]
  maxC = 0.
  #print '\nit   time   cmax   ccmax'
  for it in range(nt):
    cmax[it] = max(cmean[it,:])
    if cmax[it] > maxC:
      maxC = cmax[it]
      itMax = it 
    if cmax[it] > 0.:
     #print it,tcol[it],cmax[it],max(cvar[it,:])
     pass

  for iSmp,cM in enumerate(cmean[itMax,:]):
    if cM == cmax[itMax]:
      isMax = iSmp
      break

  #print cmean[itMax,isMax]
  #print 'Max concentration = ',maxC,' at time = ',tcol[itMax],' for it, ismp = ',itMax,isMax

  cm   = cmean[itMax,:]
  cy   = ySmp[:]*cmean[itMax,:]
  cy2  = cy[:]*ySmp[:]
  sigy = np.sqrt(sum(cy2)/sum(cm) - (sum(cy)/sum(cm))**2)

  #print 'sigY = ',sigy

  cm   = cmean[:,isMax]
  ct   = tcol[:]*cmean[:,isMax]
  ct2  = ct[:]*tcol[:]
  sigt = np.sqrt(sum(ct2)/sum(cm) - (sum(ct)/sum(cm))**2)

  #print 'sigT = ',sigt,'\n'
  #print '%s%13.5f %13.5f %13.5f %13.5f %13.5f %13.5f'%\
  #      ('Obs',maxC,np.sqrt(cvar[itMax,isMax])/maxC,sigy,sigt,dmean[idmax],np.sqrt(dvar[idmax])/dmean[idmax])

  return([maxC,np.sqrt(cvar[itMax,isMax])/maxC,sigy,sigt,\
                    dmean[idmax],np.sqrt(dvar[idmax])/dmean[idmax]])
 
def plotStat(stats=None,PGT=None,title=None,xlabel=None,ylabel=None,outFile=None):
  if stats == None or PGT == None:
    raise RuntimeError('Error: Must provide stats and PGT values')
  if not xlabel:
    xlabel = 'Observed' 
  if not ylabel:
    ylabel = 'Predicted' 
  # Plot statistical measures
  titles = [ r"$C_{max}(ppm)$", r"$\sigma_{C}/C$", r"$\sigma_{y}$", r"$\sigma_{t}$", r"$D_{max}$", r"$\sigma_{d}/D$" ]
  for ifig in range(6):
    isub = ifig%2 + 1
    if isub == 1:
      fig = plt.figure(1)
      plt.clf()
      plt.hold(True)
      if title:
        fig.text(0.35,0.87,'Comparison of DTRA PHASE I',weight='bold',fontsize=12)
        fig.text(0.32,0.82,'%s'%title,weight='bold',fontsize=12)
      else:
        fig.text(0.2,0.87,'Comparison of DTRA PHASE I Observations',weight='bold',fontsize=12)
        fig.text(0.25,0.82,'with SCIPUFF(version 2.6) Predictions',weight='bold',fontsize=12)
      plt.setp(plt.gca(), frame_on=False, xticks=(), yticks=())
    sub = fig.add_subplot(1,2,isub)
    sub.set_aspect(1)
    if np.shape(stats)[0] == 3:
      PGTcbar = sub.scatter(stats[0,ifig,:],stats[1,ifig,:],c=PGT['Indx'],marker='^')
      PGTcbar2 = sub.scatter(stats[0,ifig,:],stats[2,ifig,:],c=PGT['Indx'],marker='v')
      sub.legend([PGTcbar,PGTcbar2],['Prf 97','Prf 11'],loc=(.6,0.02))
      leg = plt.gca().get_legend()
      ltext  = leg.get_texts()
      plt.setp(ltext,fontsize=8)
      #leg.draw_frame(False)
    else:
      PGTcbar = sub.scatter(stats[0,ifig,:],stats[1,ifig,:],c=PGT['Indx'],marker='o')
    sub.plot(stats[0,ifig,:],stats[0,ifig,:])
    sub.plot(stats[0,ifig,:],stats[0,ifig,:]*2)
    sub.plot(stats[0,ifig,:],stats[0,ifig,:]*0.5)
    sub.text(.07,.9,titles[ifig],fontsize=12,transform=sub.transAxes,weight='bold')
    #sub.set_title(titles[ifig])
    if isub == 1:
      sub.set_ylabel(ylabel)
    sub.set_xlabel(xlabel)
    vmax = max(max(stats[0,ifig,:]),max(stats[1,ifig,:]))
    vmin = min(min(stats[0,ifig,:]),min(stats[1,ifig,:]))
    if ifig == 0 or ifig == 4:
      sub.set_xscale('log')
      sub.set_yscale('log')
      vmax = 10**(int(np.log10(vmax))+1)
      vmin = 10**(int(np.log10(max(vmin,1e-6))))
      sub.set_xlim([vmin,vmax])
      sub.set_ylim([vmin,vmax])
    else:
      sub.xaxis.set_major_locator(MaxNLocator(5))
      sub.yaxis.set_major_locator(MaxNLocator(5))
      sub.set_xlim([0,vmax*1.1])
      sub.set_ylim([0,vmax*1.1])
    print ifig,isub,titles[ifig]
    if isub == 2:  # Add colorbar and save the figure after 2nd subplot
      cax  = plt.axes([0.5,0.1,0.4,0.02])
      fig.text(0.35,0.1,'PGT Class',fontsize=11,weight='bold')
      plt.colorbar(PGTcbar,cax=cax,orientation="horizontal", ticks=[1,2,3,4,5,6,7])
      plt.hold(False)
      fName = 'Fig%d.pdf'%(ifig/2+1)
      plt.savefig(fName,orientation='portrait')

  Popen = subprocess.Popen
  PIPE  = subprocess.PIPE
 
  if not outFile:
    outFile = 'stats.out'
    outPDF  = 'Comparison_DTRAPHASEI.pdf'
  else:
    outPDF  = outFile.split('.')[0] + '.pdf'
  command = ["mpage","-1","-l",outFile]
  (output, errmsg) = Popen(command,stdout=open('stats.ps',"w",0),stderr=PIPE).communicate()

  command = ["gs","-dBATCH","-dNOPAUSE","-q","-sDEVICE=pdfwrite","-sOutputFile=%s"%outPDF]
  command.extend(['Fig1.pdf','Fig2.pdf','Fig3.pdf','stats.ps'])
  (output, errmsg) = Popen(command,stdout=PIPE,stderr=PIPE).communicate()

  command = ["rm","-f"]
  command.extend(['stats.ps','Fig1.pdf','Fig2.pdf','Fig3.pdf'])
  (output, errmsg) = Popen(command,stdout=PIPE,stderr=PIPE).communicate()
   
  return

def getPGT(inpDir):
  # Read Monin-Obukhov length
  PGT  = np.loadtxt(inpDir+'stability.dat',skiprows=1,dtype={'names':('Indx','L','Hflx'),'formats':('int','float','float')})
  PGClass = np.array([ 1./-5, 1./-12.5, 1./-50, 1./-1000, 1./25, 1./13, 1./5 ])
  #dPG = np.diff(PGClass)/2.
  #dPG.resize(7)
  #PGClass = PGClass + dPG
  PGT['Indx'] = PGT['Indx']*0
  ensDir = '/usr/pc/biswanath/DUGWAY PHASE1/'
  for ir in range(17): 
    ensFile = 'ENSEM%02d/R%02d-SON.txt'%(ir+1,ir+1) 
    i = -1
    for line in fileinput.input(ensDir + ensFile):
      if len(line.strip()) <= 1: 
        continue
      if line.startswith('2m'):
        i = 0
      if i >= 0:
        i += 1
        if i == 18:
          rtCb = line.rfind(')')
          print PGT['L'][ir],float(line[rtCb+1:].strip())
          PGT['L'][ir] = float(line[rtCb+1:].strip())
          fileinput.close()
          break
    for ic,iv in enumerate(PGClass):
      if 1/PGT['L'][ir] <= iv: 
        PGT['Indx'][ir] = ic + 1
        break
    if PGT['Indx'][ir] == 0: 
      PGT['Indx'][ir] = 7
    #print ir+1,PGT['Hflx'][ir],PGT['L'][ir],1/PGT['L'][ir],PGT['Indx'][ir] 
    print 'RunNo., HFlux, L = ',ir+1,PGT['Hflx'][ir],PGT['L'][ir]
  return(PGT)

# Main program for testing

if __name__ == '__main__':

  curDirList = os.getcwd().split(os.sep)
  baseDir = ''
  for dName in curDirList[1:-2]:
    baseDir = baseDir + os.sep + dName

  inpDir = baseDir + os.sep + 'Inputs' + os.sep
  metDir = baseDir + os.sep + 'metData' + os.sep + curDirList[-1] + os.sep

  print 'Input directory = ',inpDir
  print 'Met   directory = ',metDir

  env = os.environ.copy()
  tail = '\n'
  #SCIPUFF_BASEDIR="/home/user/ris/hpac/repository/scipuff/UNIX/FULL/bin/linux/gfort"
  SCIPUFF_BASEDIR="/home/user/testuserA/SCIPUFF/UNIX/FULL/bin/linux/lahey"
  env["SCIPUFF_BASEDIR"] = SCIPUFF_BASEDIR
  env["LD_LIBRARY_PATH"] = "/usr/local/lf9562/lib:/home/user/sid/HDF:%s" % SCIPUFF_BASEDIR
  hpacstub  = ["%s/hpacstub" % SCIPUFF_BASEDIR,"-I:","-M:10000"]

  PGT = getPGT(inpDir)

  for ir in range(17): 
   
    for sfx in ['inp','msc','scn','sam']:
      fName = 'r%02dm.'%(ir+1) + sfx
      shutil.copy(inpDir+fName,fName)
   
    fName = 'r%02d.'%(ir+1) + 'uaobs'
    shutil.copy(metDir+fName,fName)

    Inputs = ('r%02dm %s'%(ir+1,tail))
    #print 'Skip running hpacstub for r%02dm'%(ir+1)
    run_cmd.Command(env,hpacstub,Inputs,tail) 
    
  # Get stats from cmens and cvars files 
  outFile = open('stats.out',"w",0)
  #Adds another page so commented out
  #outFile.write('=============================================================================================%s'%tail)
  outFile.write('          Cmax         sigc/C       sigy         sigt        dmax         sigd/dmax    L%s'%tail)
  stats = np.zeros((2,6,17),float)
  for ir in range(1,18):
    cmeanFile = inpDir + 'cmens-%02d.dat'%ir
    cvarFile  = inpDir + 'cvars-%02d.dat'%ir
    outFile.write('Run %d  --------------------------------------------------------------------------------------%s'%(ir,tail))
    stats[0,:,ir-1] = np.array(getStat(cmeanFile,cvarFile),dtype=float)
    outFile.write('Obs')
    for ivar in range(6):
      outFile.write('%13.5f'%stats[0,ivar,ir-1])
    outFile.write('%s'%tail)
     # Get stats from smp files
    samFile = inpDir + 'r%02dm.sam'%ir
    smpFile = 'r%02dm.smp'%ir
    temp = 290.
    pres = 0.85518
    cScale = 1.0e+6*(22.4/42.08)*(temp/273.15)/pres 
    stats[1,:,ir-1]= getSmpStats.getStat(samFile,smpFile,cScale)
    outFile.write('Pre')
    for ivar in range(6):
      outFile.write('%13.5f'%stats[1,ivar,ir-1])
    outFile.write('%10.3f'%PGT['L'][ir-1])
    outFile.write('%s'%tail)
  outFile.close() 
  plotStat(stats=stats,PGT=PGT)

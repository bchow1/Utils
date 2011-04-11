import os
import sys
import re
import optparse
import fileinput
import subprocess
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
sys.path.append('/home/user/bnc/python')
import getSmpStats

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
  for i in range(nSmp):
    cmean[:,i] = cmData[:,i+1]*cScale
    cvar[:,i]  = cvData[:,i+1]*cScale*cScale
  cmax = np.zeros((nt),float)
  dmean = np.zeros(nSmp,float)
  dvar  = np.zeros(nSmp,float)
  dmax  = 0.
  idmax = 0
  for i in range(nSmp):
    dmean[i] = cmean[0,i]*dtcol[0]
    dvar[i]  = cvar[0,i]*dtcol[0]*dtcol[0]
    #print '\ni= ',i
    for it in range(1,nt):
      dmean[i] += cmean[it,i]*dtcol[it-1]
      dvar[i]  += cvar[it,i]*dtcol[it-1]*dtcol[it-1]
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
 

# Main program for testing

if __name__ == '__main__':

  tail = '\n'
  PGT  = np.loadtxt('stability.dat',skiprows=1,dtype={'names':('Indx','L','Hflx'),'formats':('int','float','float')})
  PGClass = [ 1./-5, 1./-12.5, 1./-50, 1./-1000, 1./25, 1./13, 1./5 ]
  PGT['Indx'] = PGT['Indx']*0
  for ir in range(17): 
    for ic,iv in enumerate(PGClass):
      if 1/PGT['L'][ir] <= iv: 
        PGT['Indx'][ir] = ic + 1
        #print ir+1,PGT[:][ir],1/PGT['L'][ir]
        break
  outFile = open('stats.out',"w",0)
  outFile.write('         Cmax          sigc/C        sigy          sigt         dmax         sigd/dmax%s'%tail)
  stats = np.zeros((2,6,17),float)
  for ir in range(1,18):
    cmeanFile = 'cmens-%02d.dat'%ir
    cvarFile  = 'cvars-%02d.dat'%ir
    outFile.write('Run %d  ------------------------------------------------------------------------------%s'%(ir,tail))
    stats[0,:,ir-1] = np.array(getStat(cmeanFile,cvarFile),dtype=float)
    outFile.write('Obs')
    for ivar in range(6):
      outFile.write('%13.5f'%stats[0,ivar,ir-1])
    outFile.write('%s'%tail)
     # Get stats from smp files
    samFile = '../../../../Inputs/Experimental/DTRAPhaseI/r%02dm.sam'%ir
    smpFile = 'r%02dm.smp'%ir
    temp = 290.
    pres = 0.85518
    cScale = 1.0e+6*(22.4/42.08)*(temp/273.15)/pres 
    stats[1,:,ir-1]= getSmpStats.getStat(samFile,smpFile,cScale)
    outFile.write('Pre')
    for ivar in range(6):
      outFile.write('%13.5f'%stats[1,ivar,ir-1])
    outFile.write('%s'%tail)
  outFile.close() 
  
  # Plot statistical measures
  titles = [ r"$C_{max}(ppm)$", r"$\sigma_{C}/C$", r"$\sigma_{y}$", r"$\sigma_{t}$", r"$D_{max}$", r"$\sigma_{d}/D$" ]
  for ifig in range(6):
    isub = ifig%2 + 1
    if isub == 1:
      fig = plt.figure(1)
      plt.clf()
      plt.hold(True)
      fig.text(0.2,0.87,'Comparison of DTRA PHASE I Observations',weight='bold',fontsize=12)
      fig.text(0.25,0.82,'with SCIPUFF(version 2.6) predictions',weight='bold',fontsize=12)
      plt.setp(plt.gca(), frame_on=False, xticks=(), yticks=())
      #fig.subplots_adjust(vspace=0.1)
      #sub = fig.add_axes([0.4,0.55,0.4,0.4])
    else:
      pass
      #sub = fig.add_axes([0.4,0.05,0.4,0.4])
    sub = fig.add_subplot(1,2,isub)
    sub.set_aspect(1)
    PGTcbar = sub.scatter(stats[0,ifig,:],stats[1,ifig,:],c=PGT['Indx'],marker='o')
    sub.plot(stats[0,ifig,:],stats[0,ifig,:])
    sub.plot(stats[0,ifig,:],stats[0,ifig,:]*2)
    sub.plot(stats[0,ifig,:],stats[0,ifig,:]*0.5)
    sub.text(.07,.9,titles[ifig],fontsize=12,transform=sub.transAxes,weight='bold')
    #sub.set_title(titles[ifig])
    if isub == 1:
      sub.set_ylabel('Predicted')
    sub.set_xlabel('Observed')
    vmax = max(max(stats[0,ifig,:]),max(stats[0,ifig,:]))
    vmin = min(min(stats[0,ifig,:]),min(stats[0,ifig,:]))
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
    if isub == 2:
      cax  = plt.axes([0.5,0.1,0.4,0.02])
      fig.text(0.35,0.1,'PGT Class',fontsize=11,weight='bold')
      plt.colorbar(PGTcbar,cax=cax,orientation="horizontal", ticks=[1,2,3,4,5,6,7])
      plt.hold(False)
      fName = 'Fig%d.pdf'%(ifig/2+1)
      plt.savefig(fName,orientation='portrait')

  Popen = subprocess.Popen
  PIPE  = subprocess.PIPE

  command = ["mpage","-1","-l","stats.out"]
  (output, errmsg) = Popen(command,stdout=open('stats.ps',"w",0),stderr=PIPE).communicate()

  command = ["gs","-dBATCH","-dNOPAUSE","-q","-sDEVICE=pdfwrite","-sOutputFile=%s"%'StatsOut.pdf','stats.ps']
  (output, errmsg) = Popen(command,stdout=PIPE,stderr=PIPE).communicate()

  command = ["gs","-dBATCH","-dNOPAUSE","-q","-sDEVICE=pdfwrite","-sOutputFile=%s"%'Comparison_DTRAPHASEI.pdf']
  command.extend(['Fig1.pdf','Fig2.pdf','Fig3.pdf','StatsOut.pdf'])
  (output, errmsg) = Popen(command,stdout=PIPE,stderr=PIPE).communicate()

  command = ["rm","-f"]
  command.extend(['stats.out','stats.ps','Fig1.pdf','Fig2.pdf','Fig3.pdf','StatsOut.pdf'])
  (output, errmsg) = Popen(command,stdout=PIPE,stderr=PIPE).communicate()

  ''' 
# Parse arguments
  arg = optparse.OptionParser()
  arg.add_option("-m",action="store",type="string",dest="cmeanFile")
  arg.add_option("-v",action="store",type="string",dest="cvarFile")
  opt,args = arg.parse_args()
  # Check arguments
  if opt.cmeanFile and opt.cvarFile:
    cmeanFile = opt.cmeanFile
    cvarFile  = opt.cvarFile
  else:
    if not opt.cmeanFile:
      print 'Error: cmeanFile must be specified'
    if not opt.cvarFile:
      print 'Error: cvarFile must be specified'
    print 'Usage: getObsStats.py -m cmeanFile -v cvarFile'
    sys.exit()
   '''

import os
import sys
import re
import optparse
import fileinput
import numpy as np
from matplotlib import pyplot as plt

# Search patterns    
pattSmpT  = re.compile("(HPAC)|(SCIPUFF)\s*",re.I)  # Sampler type
pattSmp1  = re.compile("(.+)001")                   # First sampler

def getStat(samFile,smpFile,cScale=1.,yCol=1,lPrint=None):

  # Read samfile
  smpLoc = []
  for line in fileinput.input( samFile ):
    #print fileinput.lineno(),': ',line
    if fileinput.isfirstline():
      sam4Type = pattSmpT.match(line)
    else:
      if len(line) < 3: break
      smpLoc.append(line.split()[0:3])
  fileinput.close()
  smpLoc = np.array(smpLoc,dtype=float)
  xCol = 1-yCol
  xSmp = np.array(smpLoc[:,xCol],dtype=float)
  ySmp = np.array(smpLoc[:,yCol],dtype=float)
  zSmp = np.array(smpLoc[:,2],dtype=float)
  nSmp = len(smpLoc)
  #print 'Number of samplers = ',nSmp

  # Read smpFile
  smpLoc = []
  if sam4Type:
   nSkipRows = 1
   for line in fileinput.input( smpFile ):
     if fileinput.isfirstline():
       smpHead = line 
     else:
       break
  else:
   smpHead = ''
   for line in fileinput.input( smpFile ):
     if fileinput.isfirstline():
       nvs = int(line.strip())
       nSkipRows = nvs/10 + 3
     elif fileinput.lineno() < nSkipRows:
       smpHead = smpHead + ' ' + line.strip()
       continue
     else:
      break
  fileinput.close()
  smpHead = smpHead.split()
  #print smpHead
  nVar = 0
  for vName in smpHead:
    if vName.endswith('001'):
      nVar += 1
  print 'nVar = ',nVar,'nSkipRows = ',nSkipRows
  if nVar < 3:
    print 'Error: Need time scale for dosage'
    return (0.,0.,0.,0.,0.,0.)
  #
  cdata = np.loadtxt(smpFile,skiprows=nSkipRows)
  tcol  = cdata[:,0]
  nt = len(tcol)
  cmean = np.zeros((nt,nSmp),float)
  cvar  = np.zeros((nt,nSmp),float)
  clen  = np.zeros((nt,nSmp),float)
  for i in range(nSmp):
    cmean[:,i] = cdata[:,i*nVar+1]*cScale
    cvar[:,i]  = cdata[:,i*nVar+2]*cScale*cScale
    clen[:,i]  = cdata[:,i*nVar+3]
  
  # convert to m
  ySmp = ySmp*1e3
  maxC,sigCbyC,sigY,sigT,maxD,sigDbyD = calcStat(tcol,cmean,cvar,ySmp,clen=clen)
  if lPrint:
    print 'maxC, sigCbyC,sigY,sigT,maxD,sigDbyD'
    print '%s%13.5f %13.5f %13.5f %13.5f %13.5f %13.5f'%\
          ('Pre',maxC,sigCbyC,sigY,sigT,maxD,sigDbyD)

  return (maxC,sigCbyC,sigY,sigT,maxD,sigDbyD)

def calcStat(tcol,cmean,cvar,ySmp,clen=None,dmean=None,dvar=None):

  if clen is None and dmean is None:
    print 'Error: Must provide timescale or dosage mean for dosage calculations'
    return (0.,0.,0.,0.,0.,0.)
  (nt,nSmp) = np.shape(cmean)
  dtcol = np.diff(tcol)
  cmax = np.zeros((nt),float)
  if clen is not None:
    dmean = np.zeros(nSmp,float)
    dvar  = np.zeros(nSmp,float)
    for i in range(nSmp):
      dmean[i] = cmean[0,i]*dtcol[0]
      dvar[i]  = cvar[0,i]*dtcol[0]*clen[0,i]
      for it in range(1,nt):
        dmean[i] += cmean[it,i]*dtcol[it-1]
        dvar[i]  += cvar[it,i]*dtcol[it-1]*clen[it,i]
  dmax  = max(dmean)
  idmax = np.where(dmean == dmax)[0][0]
  print '\n','Max dosage and variance = ',dmean[idmax], dvar[idmax],' for ismp = ',idmax

  maxC = np.max(cmean)
  its = np.where(cmean==maxC)
  itMax = its[0][0]
  isMax = its[1][0]
  if clen is not None:
    print 'Max concentration, variance and scale = ',maxC,cvar[itMax,isMax],clen[itMax,isMax]
  else:
    print 'Max concentration, variance, dosage and dosage variance  = ',maxC,cvar[itMax,isMax],dmean[itMax,isMax],dvar[itMax,isMax]
  print ' at time = ',tcol[itMax],' for it, ismp = ',itMax,isMax,'\n'

  cm    = cmean[itMax,:]
  cmi   = sum(cm)
  cy    = ySmp[:]*cmean[itMax,:]
  ybar  = sum(cy)/cmi
  
  cy2  = cy[:]*ySmp[:]
  sigy = np.sqrt(sum(cy2)/cmi - ybar**2)

  cm   = cmean[:,isMax]
  cmi  = sum(cm)
  ct   = tcol[:]*cmean[:,isMax]
  tbar = sum(ct)/cmi
  ct2  = ct[:]*tcol[:]
  sigt = np.sqrt(sum(ct2)/cmi - tbar**2)

  return([maxC,np.sqrt(cvar[itMax,isMax])/maxC,sigy,sigt,
         dmean[idmax],np.sqrt(dvar[idmax])/dmean[idmax]])

# Main program for testing

if __name__ == '__main__':

  #for ir in range(1,18):
  #  samFile = '../../../../Inputs/Experimental/DTRAPhaseI/r%02dm.sam'%ir
  #  smpFile = 'r%02dm.smp'%ir
  samFile = 'r01m.sam'
  smpFile = 'r01m.smp'
  temp = 290.
  pres = 0.85518
  cScale = 1.0e+6*(22.4/42.08)*(temp/273.15)/pres 
  print 'Get stats from ',smpFile
  getStat(samFile,smpFile,cScale,lPrint=True)

  '''
  # Parse arguments
  arg = optparse.OptionParser()
  arg.add_option("-p",action="store",type="string",dest="prjName")
  arg.add_option("-a",action="store",type="string",dest="samFile")
  arg.add_option("-s",action="store",type="float",dest="cScale")
  arg.set_defaults(prjName=None,samFile=None,cScale=1.)
  opt,args = arg.parse_args()
  # Check arguments
  if not opt.prjName:
    print 'Error: prjName must be specified'
    print 'Usage: getSmpStats.py -p prjName [-a prj.sam -s cScale]'
    sys.exit()
  else:
    smpFile = opt.prjName + '.smp'
    if not os.path.exists(smpFile):
      print 'Error: Cannot find smpFile',smpFile
  if opt.samFile:
    samFile = opt.samFile
    print 'samFile from command line will be used'
  else:
    samFile = opt.prjName + '.sam'
    if not os.path.exists(samFile):
      print 'Error: Cannot find samFile',samFile
  if opt.cScale:
    cScale = opt.cScale
  getStat(samFile,smpFile,cScale)
  '''


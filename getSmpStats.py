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

def getStat(samFile,smpFile,cScale=1.):

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
  xSmp = np.array(smpLoc[:,0],dtype=float)
  ySmp = np.array(smpLoc[:,1],dtype=float)
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
  #print 'nVar = ',nVar,'nSkipRows = ',nSkipRows
  #
  cdata = np.loadtxt(smpFile,skiprows=nSkipRows)
  tcol  = cdata[:,0]
  dtcol = np.diff(tcol)
  nt = len(tcol)
  cmean = np.zeros((nt,nSmp),float)
  cvar  = np.zeros((nt,nSmp),float)
  for i in range(nSmp):
    cmean[:,i] = cdata[:,i*nVar+1]*cScale
    cvar[:,i]  = cdata[:,i*nVar+2]*cScale*cScale
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

  maxC  = 0.
  # print '\nit   time   cmax   ccmax'
  for it in range(nt):
    cmax[it] = max(cmean[it,:])
    if cmax[it] > maxC:
      maxC = cmax[it]
      itMax = it 
    #if cmax[it] > 0.:
     #print it,tcol[it],cmax[it],max(cvar[it,:])
     #print cmean[it,:]
     #print cvar[it,:]

  for iSmp,cM in enumerate(cmean[itMax,:]):
    if cM == cmax[itMax]:
      isMax = iSmp
      break

  #print '\n','Max concentration = ',maxC,' at time = ',tcol[itMax],' for it, ismp = ',itMax,isMax

  cm   = cmean[itMax,:]
  cy   = ySmp[:]*cmean[itMax,:]
  cy2  = cy[:]*ySmp[:]
  sigy = np.sqrt(sum(cy2)/sum(cm) - (sum(cy)/sum(cm))**2)
  #print 'sigY = ',sigy*1.e3      # Convert to m

  cm   = cmean[:,isMax]
  ct   = tcol[:]*cmean[:,isMax]
  ct2  = ct[:]*tcol[:]
  sigt = np.sqrt(sum(ct2)/sum(cm) - (sum(ct)/sum(cm))**2)

  #print 'sigT = ',sigt
  print '%s%13.5f %13.5f %13.5f %13.5f %13.5f %13.5f'%\
        ('Pre',maxC,np.sqrt(cvar[itMax,isMax])/maxC,sigy*1e3,sigt,dmean[idmax],np.sqrt(dvar[idmax])/dmean[idmax])

  return([maxC,np.sqrt(cvar[itMax,isMax])/maxC,sigy*1e3,sigt,
         dmean[idmax],np.sqrt(dvar[idmax])/dmean[idmax]])

# Main program for testing

if __name__ == '__main__':

  for ir in range(1,18):
    samFile = '../../../../Inputs/Experimental/DTRAPhaseI/r%02dm.sam'%ir
    smpFile = 'r%02dm.smp'%ir
    temp = 290.
    pres = 0.85518
    cScale = 1.0e+6*(22.4/42.08)*(temp/273.15)/pres 
    getStat(samFile,smpFile,cScale)

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


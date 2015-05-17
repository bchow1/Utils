import os
import sys
import re
import shutil
import socket
import subprocess
import fileinput
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

compName = socket.gethostname()
env      = os.environ.copy()

# Local modules
if compName == 'sm-bnc' or compName == 'sage-d600':
  sys.path.append('C:\\Users\\sid\\python')

if compName == 'pj-linux4':
  sys.path.append('/home/user/bnc/python')
  
def runPrj(basePrj,ntList):

  if os.sys.platform == 'win32':
    binDir      = "D:\\SCIPUFF\\CVS_REPO\\workspace\\DTRA\\vs2008_Reverse\\bin\\intel\\Win32\\Debug"
    vendir      = "D:\\SCIPUFF\\CVS_REPO\\bin\\vendor\\Win32" 
    iniFile     = "D:\\SCIPUFF\\CVS_REPO\\workspace\\DTRA\\vs2008\\scipuff.ini"
    runDir      = 'D:\\SrcEst\\P1\\runs\\Outputs\\OnlySimple\\Simple\\simplei'
    env["PATH"] = "%s;%s;%s" % (binDir,vendir,env["PATH"])
    runsci       = os.path.join(binDir,'runsci.exe')
  else:
    binDir      = "/home/user/bnc/scipuff/Repository/UNIX/AFTACx64_OMP/bin/linux/ifort"
    iniFile     = "scipuff.ini"
    runDir      = '/home/user/bnc/scipuff/runs/AFTAC/OpenMP/stLouis2'
    env["PATH"] = "%s:%s" % (binDir,env["PATH"])
    runsci       = os.path.join(binDir,'runsci')
    runsci      = os.path.join(binDir,'runsci')

  os.chdir(runDir)
  print 'Using runsci from ',binDir,' in ',runDir,'\n'
  print env["PATH"],'\n'

  
  prjNames = []
  sfxList = ['inp','scn','msc']
  for iproc,nproc in enumerate(ntList): 
    prjName = '%s_p%d'%(basePrj,nproc)
    prjNames.append(prjName)
    for sfx in sfxList:
      shutil.copy(basePrj+'.'+sfx,prjName+'.'+sfx)
    iniFile = 'scipuff_p%d.ini'%nproc
    shutil.copy(iniFile,'scipuff.ini')
    runSCI(env,runsci,prjName,iniFile)

def crtNpArray(prjNames):
  for prjNo,prjName in enumerate(prjNames):
    nPuffs = countPuffs(prjName)
    print prjName,np.shape(nPuffs)
    if prjName == prjNames[0]:
      nt = len(nPuffs)
      print nt,len(prjNames)+1
      npArray = np.zeros((nt,len(prjNames)+1))
      npArray[:,0] = nPuffs[:,0]
      npArray[:,1] = nPuffs[:,1]
    else:
      nt = min(nt,np.shape(nPuffs)[0])
      npArray[:nt,prjNo+1] = nPuffs[:nt,1] -  npArray[:nt,1]
  return npArray
  prtNPuff(prjNames,npArray)
  
def prtNPuff(prjNames,npArray):
  sys.stdout.write('Hr ')
  for prj in prjNames:
    sys.stdout.write('%s '%prj)
    if prj != prjNames[-1]:
      sys.stdout.write(', ')
  sys.stdout.write('\n')
  for npuf in npArray:
    sys.stdout.write('%3.1f, '%npuf[0])
    for iproj,prjName in enumerate(prjNames):
      sys.stdout.write(' %5d'%npuf[iproj+1])
      if prjName != prjNames[-1]:
        sys.stdout.write(', ')      
    sys.stdout.write('\n')

def runSCI(env,runsci,prjName,iniFile):

  print 'Running runsci for %s using %s'%(prjName,iniFile)
  
  #if os.path.exists(outFile):
  #  os.remove(outFile)
  
  runsci_inp = open('runsci.input','w') 
  runsci_inp.write('./\n%s\n'%prjName)
  runsci_inp.close()

  runsci_inp = open('runsci.input','r')
  runsci_out = open('runsci.output','w')
  runsci_err = open('runsci.error','w')
  h = subprocess.Popen(runsci, env=env, bufsize=0, shell=False,stdin=runsci_inp, stdout=runsci_out,stderr=runsci_err)
  h.communicate()
  runsci_inp.close()
  runsci_out.close()
  runsci_err.close()
      
  # Cleanup
  #os.remove('runsci.input')
  #os.remove('runsci.output')
  #os.remove('runsci.error')

def countPuffs(prjName):
  pattNpuff = re.compile('.*\s+t\s*=\s*(\d*\.\d*)\s*.*\s+NPUFF\s*=\s*(\d+).*',re.I)
  pattCmplt = re.compile('.*\s+Time\s*=\s*(\d*\.\d*)\s*.*',re.I)

  prjLog  = prjName + '.log'
  nPuffs = []
  if os.path.exists(prjLog):
    for line in fileinput.input(prjLog):
      if line.startswith("Output completed at"):
        matchNpuff = pattNpuff.match(line.strip())
        if matchNpuff:
          nPuffs.append(map(float,(matchNpuff.group(1),matchNpuff.group(2))))
      #if line.startswith('Normal termination'):
      #  matchCmplt = pattCmplt.match(line.strip())              
      #  print 'Normal',float(matchCmplt.group(1))
  else:
    print 'Missing :',prjLog 
  nPuffs = np.array(nPuffs)       
  return nPuffs

def pltnPuffs(nPuffs,ip,ntList):
  
  global Lh,Lk
  
  lSty = ['-','--','-.',':']
  mSty = ['o','s','d','*']
  nproc = ntList[ip]

  if nproc == ntList[0]:
    fig = plt.figure(1)
    plt.clf()
    plt.hold(True)
    Lh = []
    Lk = []

  lh, = plt.plot(nPuffs[:,0],nPuffs[:,1],marker=mSty[ip],linestyle=lSty[ip])
  Lh.append(lh)
  Lk.append('No. Procs = %d'%nproc)

  if nproc == ntList[-1]:
    plt.xlabel('Time')
    plt.ylabel('No. of Puffs')
    plt.legend(Lh,Lk)
    plt.hold(False)
    #plt.show()
    plt.savefig('NP_%d-%d.png'%(ntList[0],nproc))

  return

if __name__ == '__main__':
  ntList = [1,4]
  basePrj = 'stLouis'
  runPrj(basePrj,ntList) 
  prjNames  = ['stLouis_p1','stLouis_p4','win_p1','win_p4','sL08_t1','sL08_t4']
  npArray = crtNpArray(prjNames)
  prtNPuff(prjNames,npArray)
  #nPuffs = countPuffs(prjName)
  #pltnPuffs(nPuffs,iproc,ntList) 

import os
import sys
import shutil
import socket
import run_cmd
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
  runDir    = 'D:\\SrcEst\\P1\\runs\\Outputs\\OnlySimple\\Simple\\simplei'

if compName == 'pj-linux4':
  sys.path.append('/home/user/bnc/python')
  runDir = '/home/user/bnc/TestHPAC/Outputs/140902_OMP_p1/Experimental/Etex'
  
os.chdir(runDir)

def mainProg():
  
  if os.sys.platform != 'win32':
    binDir      = "/home/user/testuserP/SCIPUFF/UNIX/FULLx64_OMP/bin/linux/ifort"
    iniFile     = "/home/user/bnc/hpac/SCIPUFF/UNIX/FULL/bin/linux/scipuff.ini"
    env["PATH"] = "%s:%s" % (binDir,env["PATH"])
    scipp       = os.path.join(binDir,'scipp')
  else:
    binDir      = "D:\\SCIPUFF\\CVS_REPO\\workspace\\DTRA\\vs2008_Reverse\\bin\\intel\\Win32\\Debug"
    vendir      = "D:\\SCIPUFF\\CVS_REPO\\bin\\vendor\\Win32" 
    iniFile     = "D:\\SCIPUFF\\CVS_REPO\\workspace\\DTRA\\vs2008\\scipuff.ini"
    env["PATH"] = "%s;%s;%s" % (binDir,vendir,env["PATH"])
    scipp       = os.path.join(binDir,'scipp.exe')
  print 'Using scipp from ',binDir
  print scipp
  print env["PATH"]
  
  prjName = 'etex_cux_p1_nosmfld'
  (tSmp1,cInst1,cAvrg1,tDos1,cDos1) = runSCIPP(env,scipp,prjName,iniFile)

  prjName = 'etex_cux_p2_nosmfld'
  (tSmp2,cInst2,cAvrg2,tDos2,cDos2) = runSCIPP(env,scipp,prjName,iniFile)
  
  fig = plt.figure(1)
  plt.clf()
  
  nSkip = 1
  
  tDos1 = tDos1 - 1.5
  tDos2 = tDos2 - 1.5
  
  hI1, = plt.semilogy(tSmp1[::nSkip],cInst1[::nSkip],marker='^',linestyle='None',\
               markerfacecolor='None',markeredgecolor='red')
  hA1, = plt.semilogy(tSmp1[::nSkip],cAvrg1[::nSkip],marker='s',linestyle='None',\
               markerfacecolor='None',markeredgecolor='red')
  hD1, = plt.semilogy(tDos1,cDos1,marker='o',linestyle='None',\
               markerfacecolor='None',markeredgecolor='red')
  
  hI2, = plt.semilogy(tSmp2[::nSkip],cInst2[::nSkip],marker='^',linestyle='None',\
               markerfacecolor='None',markeredgecolor='green')
  hA2, = plt.semilogy(tSmp2[::nSkip],cAvrg2[::nSkip],marker='s',linestyle='None',\
               markerfacecolor='None',markeredgecolor='green')
  hD2, = plt.semilogy(tDos2,cDos2,marker='o',linestyle='None',\
               markerfacecolor='None',markeredgecolor='green')
  
  plt.ylim([1.e-20,1e-10]) 
  plt.legend((hI1,hA1,hD1,hI2,hA2,hD2),('Inst1','Avg1','Dos1','Inst2','Avg2','Dos2'),ncol=1,bbox_to_anchor=(0.98,0.98))
  #plt.show()
  plt.savefig('p1_p2_90hr_nosmfld.png')  

  ax = plt.gca()
  ax.relim()
  plt.xlim([28.,52.])
  plt.ylim([1.e-15,1e-11]) 
  plt.draw() 
  plt.savefig('p1_p2_10hr_nosmfld.png')
  
  
def runSCIPP(env,scipp,prjName,iniFile):
  
  global timeList

  #-- Run scipp fo project
  print 'Running scipp on project ',prjName
  
  outFile = prjName + '_scipp' + '.out'    
  crtOut(scipp,iniFile,prjName,'0',outFile,rmOut=False)      
  os.remove(outFile)
  
  timeLStart = 9999
  timeList   = []
  for line in fileinput.input('scipp.output'):
    #print fileinput.lineno(),': ',line
    if 'Available Field Times' in line:
      timeLStart = fileinput.lineno() + 1
      print timeLStart
    if fileinput.lineno() > timeLStart:
      if len(line.strip()) == 0:
        print 'Break'
        break      
      timeList.append(line.split('(')[1].split(')')[0].strip())
  fileinput.close()
  os.remove('scipp.output')    
  #print timeList
  
  # Dosage
  dosList = []
  for tNo,tString in enumerate(timeList):
    outFile = prjName + '_%d.out'%tNo
    crtOut(scipp,iniFile,prjName,tString,outFile)
    mdos,vdos = np.loadtxt(outFile,skiprows=13,usecols=(2,3))
    dosList.append([(tNo+1)*3.,mdos,0.])
  dosList = np.array(dosList)
  dosDiff = np.diff(dosList[:,1])
  dosList[1:,2] = dosDiff/(3.*3600.)
  print dosList
  
  # Sampler values
  smpVals = np.loadtxt(prjName +'.smp' ,skiprows=1,usecols=(0,1,4,0))
  print 'SMP\n',smpVals
  smpDiff = np.diff(smpVals,axis=0)
  smpVals[0,3]  = 0.
  smpVals[1:,3] = smpDiff[:,2]/smpDiff[:,0]
  smpVals[:,0]  = smpVals[:,0]/3600.
  for row in range(len(smpVals)):
    print row,smpVals[row,:]
  
  # 
  tSmp   = smpVals[:,0]
  cInst  = smpVals[:,1]
  cAvrg  = smpVals[:,3]
  tDos   = dosList[:,0] 
  cDos   = dosList[:,2]

  return (tSmp,cInst,cAvrg,tDos,cDos)

def crtOut(scipp,iniFile,prjName,tString,outFile,rmOut=True):
        
  
    inSCIpp = open('scipp.input','w') 
    inSCIpp.write('%s\n'%iniFile)
    inSCIpp.write('KE\n%s\n'%prjName)
    
    # Surface Dosage
    inSCIpp.write('Surface Dosage \nMean\n')
    inSCIpp.write('%s\n'%tString)
    inSCIpp.write('CG \n1 \n8.7 53.866 \n')
    
    
    inSCIpp.write('%s\n'%outFile)    
    inSCIpp.close()
    
    if os.path.exists(outFile):
      os.remove(outFile)
    
    scipp_inp = open('scipp.input','r')
    scipp_out = open('scipp.output','w')
    scipp_err = open('scipp.error','w')
    h = subprocess.Popen(scipp, env=env, bufsize=0, shell=False,stdin=scipp_inp, stdout=scipp_out,stderr=scipp_err)
    h.communicate()
    scipp_inp.close()
    scipp_out.close()
    scipp_err.close()
        
    # Cleanup
    os.remove('scipp.input')
    if rmOut:
      os.remove('scipp.output')
    os.remove('scipp.error')
           
if __name__ == '__main__':
    mainProg() 
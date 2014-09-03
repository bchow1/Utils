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
  scriptDir = 'D:\\SrcEst\\P1\\script'
  runDir    = 'D:\\SrcEst\\P1\\runs\\Outputs\\OnlySimple\\Simple\\simplei'

if compName == 'pj-linux4':
  sys.path.append('/home/user/bnc/python')
  scriptDir = '/home/user/bnc/SrcEst/P1/script'
sys.path.append(scriptDir)
os.chdir(runDir)

def mainProg():
  
  if os.sys.platform != 'win32':
    binDir      = "/home/user/bnc/hpac/SCIPUFF/UNIX/FULL/bin/linux/gfort"
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
  
  rType   = 'INST'
  prjName = 'simplei'
  getsrcFunc(env,scipp,prjName,iniFile,rType)
  
def getsrcFunc(env,scipp,prjName,iniFile,rType):
  
  global timeList

  #-- Run scipp on reverse run for given release type
  print 'Running scipp on project ',prjName,' for type ',rType
  
  if rType == 'CONT':
    pass
  else:
    sclFile = prjName + '_' + rType + '.scl'    
    crtScl(scipp,iniFile,prjName,'User time',sclFile,rmOut=False)      
    os.remove(sclFile)
    
    timeLStart = 9999
    timeList   = []
    for line in fileinput.input('scipp.output'):
      if 'Available Field Times' in line:
        timeLStart = fileinput.lineno() + 1
      if 'User time' in line:
        break
      if fileinput.lineno() > timeLStart:
        timeList.append(line.split('(')[1].split(')')[0].strip())
    fileinput.close()
    os.remove('scipp.output')    
    timeList.reverse()
    #print timeList
    
    sfnMax = np.zeros((2,len(timeList)),float)
    scale  = np.zeros(1,dtype={'names':['scl','hit','null'],'formats':['float','float','float']})
    
    for tNo,tString in enumerate(timeList):
      print tNo,tString
      sclFile = prjName + '_' + rType + '_%d.scl'%tNo
      #crtScl(scipp,iniFile,prjName,tString,sclFile)
      sfnMax[0,tNo] = tNo
      if tNo == 0: 
        dType,sfnMax[1,tNo] = pltScl(sclFile,tNo)
      else:
        dType,sfnMax[1,tNo] = pltScl(sclFile,tNo,dType=dType)
      #break
    scale['scl'] = sfnMax[1,:].max()
    print scale['scl']
    
    # Scaled
    for tNo,tString in enumerate(timeList):
      sclFile = prjName + '_' + rType + '_%d.scl'%tNo
      dType,sfnMax[1,tNo] = pltScl(sclFile,tNo,dType=dType,scale=scale)
    fig = plt.figure(1)
    plt.clf()
    plt.scatter(sfnMax[0,:],sfnMax[1,:])
    plt.show()

  return

def crtScl(scipp,iniFile,prjName,tString,sclFile,rmOut=True):
          
    sfnFile  = sclFile.replace('.scl','.sfn')
    
    inSCIpp = open('scipp.input','w') 
    inSCIpp.write('%s\n'%iniFile)
    inSCIpp.write('KE\n%s\n'%prjName)
    inSCIpp.write('Adjoint Concentration\nSource Location Prob\n')
    # slice lower, left; upper, right; Slice height
    inSCIpp.write('%s\n\n\n\n'%tString)
    inSCIpp.write('AG\n1e-30\n100 100\n')
    inSCIpp.write('%s\n'%sfnFile)
    inSCIpp.close()
    
    if os.path.exists(sfnFile):
      os.remove(sfnFile)
    if os.path.exists(sclFile):
      os.remove(sclFile)
    
    scipp_inp = open('scipp.input','r')
    scipp_out = open('scipp.output','w')
    scipp_err = open('scipp.error','w')
    h = subprocess.Popen(scipp, env=env, bufsize=0, shell=False,stdin=scipp_inp, stdout=scipp_out,stderr=scipp_err)
    h.communicate()
    scipp_inp.close()
    scipp_out.close()
    scipp_err.close()
    
    try:
      shutil.move('fort.77',sclFile)
      print '\nMove %s to %s'% ('fort.77',sclFile)
    except EnvironmentError:
      raise
    
    # Cleanup
    os.remove(sfnFile)
    os.remove('scipp.input')
    if rmOut:
      os.remove('scipp.output')
    os.remove('scipp.error')

def pltScl(sclFile,tNo,dType=None,scale=None):
  
  global timeList
  
  for line in fileinput.input(sclFile):
    if fileinput.lineno() == 1:
      nList = line.split(',')
      for vNo,val in enumerate(nList):
        nList[vNo] = int(val.split('=')[1])
      nxy, nHit, nNull = nList
      break
  fileinput.close()
  
  nCols   = 2 + nHit + nNull + 2
  ny      = np.sqrt(nxy)
  nx      = ny
  npzFile = 'Slf%03d.npz'%tNo
    
  if dType is None:
    print nxy, nHit, nNull
    colNames = ['x','y']
    for i in range(nHit):
      colNames.extend(['T%03d'%i])
    for i in range(nNull):
      colNames.extend(['N%03d'%i])
    colNames.extend(['Slf','Mass'])
    colFmt = []
    for iCol in range(nCols):
      colFmt.extend(['float'])
    print colNames
    #print colFmt
    dType = {'names':colNames,'formats':colFmt}
    #print dType

  cMin = 0.01
  cMax = 1.01
  levels = np.linspace(cMin,cMax,num=6)
  if tNo == 0:
    print levels
  
  lnorm  = colors.Normalize(levels,clip=False)
  lScatter = True
    
  if os.path.exists(npzFile) and scale is not None:
    
    sclDat = np.load(npzFile)
    x   = sclDat['arr_0']
    y   = sclDat['arr_1']
    scl = sclDat['arr_2']/scale['scl'] 

    fig = plt.figure(1)
    plt.clf()
    cf = plt.contourf(x,y,scl,levels)
    plt.colorbar(cf)
    timeStr = timeList(tNo).split()[2]
    plt.title('Time %s'%timeStr)
    plt.savefig('Slf%s.png'%timeStr)
    
  else: 
    
    sclDat = np.loadtxt(sclFile,skiprows=1,dtype=dType)
    scl    = np.transpose(sclDat['Slf'].reshape(np.sqrt(nxy),-1))
    x      = sclDat['x'][::ny]
    y      = sclDat['y'][:ny]
    np.savez(npzFile,x,y,scl)
        
    cncH = np.zeros((nx,ny,nHit),float)
    cncN = np.zeros((nx,ny,nNull),float)
    #print sclDat.dtype[0],len(sclDat.dtype)
    cnc_view = sclDat.view((sclDat.dtype[0],len(sclDat.dtype)))
    #print np.shape(cnc_view),sclDat.dtype.names[2:nHit+2]
    
    hMax = cnc_view[:,2:2+nHit].max()
    nMax = cnc_view[:,2+nHit:2+nHit+nNull].max() 
    print 'Max Conc for hit and null = ',hMax,nMax
    
    if lScatter:
      for i in range(nHit):
        colName = 'T%03d'%i
        sclDat[colName] = sclDat[colName]/hMax
        if sclDat[colName].max() < 1.e-2:
          continue
        fig = plt.figure(1)
        plt.clf()
        plt.hold(True)
        #print sclDat['x']
        #print sclDat['y']
        #print sclDat[colName].min(), sclDat[colName].max(),i+2,':',colName,cnc_view[:,i+2].max()
        cf = plt.scatter(sclDat['x'],sclDat['y'],c=sclDat[colName],edgecolors='none',cmap=plt.cm.jet,vmin=cMin,vmax=cMax)
        cf.cmap.set_under('white')
        cf.set_clim(cMin,cMax)
        cbar = plt.colorbar(cf,ticks=levels,format="%3.1f")
        cbar.ax.set_yticklabels(levels-0.01)
        timeStr = timeList(tNo).split()[2]
        plt.savefig('Slf%s_hits.png'%timeStr)        
        plt.title('Hit Concentration at Time %s'%timeStr)
        plt.hold(False)
        plt.savefig('Slf%03d_%03d_nulls.png'%(tNo,i))
      for i in range(nNull):
        colName = 'N%03d'%i
        sclDat[colName] = sclDat[colName]/hMax
        if sclDat[colName].max() < 1.e-2:
          continue
        fig = plt.figure(1)
        plt.clf()
        plt.hold(True)
        cf = plt.scatter(sclDat['x'],sclDat['y'],c=sclDat[colName],edgecolors='none',cmap=plt.cm.jet,vmin=cMin,vmax=cMax)
        cf.cmap.set_under('white')
        cf.set_clim(cMin,cMax)
        cbar = plt.colorbar(cf,ticks=levels,format="%3.1f")
        cbar.ax.set_yticklabels(levels-0.01)
        timeStr = timeList(tNo).split()[2]
        plt.savefig('Slf%s_nulls.png'%timeStr)        
        plt.title('Null Concentration at Time %s'%timeStr)
        plt.hold(False)
        plt.savefig('Slf%03d_%03d_nulls.png'%(tNo,i))                   
    else:
      for i in range(nHit):
        cncH[:,:,i] = np.transpose(sclDat[colName].reshape(np.sqrt(nxy),-1))/hMax
        if cncH[:,:,i].max() < 0.01:
          continue             
        fig = plt.figure(1)
        plt.clf()
        plt.hold(True)
        cf = plt.contourf(x,y,cncH[:,:,i],norm=lnorm,levels=levels,cmap=plt.cm.jet,vmin=cMin,extend='both')
        cf.cmap.set_under('white')
        cf.set_clim(cMin,cMax)
        cs = plt.contour(x,y,cncH[:,:,i],norm=lnorm,levels=levels,colors='k')
        plt.grid(b=True, which='major', color='k',linestyle='-')
        cbar = plt.colorbar(cf,ticks=levels,format="%3.1f")
        cbar.ax.set_yticklabels(levels-cMin)
        plt.title('Time %s'%str(tNo))
        plt.hold(False)
        plt.savefig('Slf%03d_%03d_hits.png'%(tNo,i)) 
                                                   
      for i in range(nNull):
        colName = 'N%03d'%i
        cncN[:,:,i] = np.transpose(sclDat[colName].reshape(np.sqrt(nxy),-1))/nMax         
        if cncN[:,:,i].max() < cMin:
          continue
        fig = plt.figure(1)
        plt.clf()
        plt.hold(True) 
        cf = plt.contourf(x,y,cncN[:,:,i],norm=lnorm,levels=levels,cmap=plt.cm.jet,vmin=cMin,extend='both')
        cf.cmap.set_under('white')
        cf.set_clim(cMin,cMax)
        cs = plt.contour(x,y,cncN[:,:,i],norm=lnorm,levels=levels,colors='k')
        plt.grid(b=True, which='major', color='k',linestyle='-')
        cbar = plt.colorbar(cf,ticks=levels,format="%3.1f")
        cbar.ax.set_yticklabels(levels-cMin)
        plt.title('Time %s'%str(tNo))
        plt.hold(False)
        plt.savefig('Slf%03d_%03d_nulls.png'%(tNo,i))
    
  return dType,scl.max()
           
if __name__ == '__main__':
    mainProg() 
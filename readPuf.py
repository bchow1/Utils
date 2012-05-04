#
import os
import sys
import subprocess
import fileinput
import numpy as np
import matplotlib.pyplot as plt
#
import run_cmd
import setSCIparams as SCI 

env = os.environ.copy()
if sys.platform == 'win32':
  SCIPUFF_BASEDIR="D:\\hpac\\SCIPUFF\\bin"
  compiler = 'intel'
  version = 'debug'
  OldPath = env["PATH"]
  bindir = SCIPUFF_BASEDIR + "\\" + compiler + "\\" + version
  urbdir = SCIPUFF_BASEDIR + "\\" + compiler + "\\nonurban"  + "\\" + version
  vendir = SCIPUFF_BASEDIR + "\\vendor" 
  env["PATH"] = "%s;%s;%s;%s" % (bindir,urbdir,vendir,OldPath)
  print env["PATH"]
  scipp  = ["%s\\scipp.exe" % bindir,"-I:"]
  #scipp = ["scipp.exe","-I:"]
  tail = '\r\n'
else:
  SCIPUFF_BASEDIR = "/home/user/bnc/hpac/fromSCIPUFF/Repository/UNIX/FULL/bin/linux/lahey"
  scipp = ["%s/postprocess" % SCIPUFF_BASEDIR,"-I:"]
  env["LD_LIBRARY_PATH"] = "/usr/local/lf9562/lib:/home/user/bnc/gfortran/x86_32:/home/user/bnc/sqlite3/flibs-0.9/lib/gfort:/home/user/sid/HDF"
  env["LD_LIBRARY_PATH"] = env["LD_LIBRARY_PATH"] + ':' + SCIPUFF_BASEDIR
  tail = '\n'

#myEnv = SCI.setEnv(SCIPUFF_BASEDIR=SCIPUFF_BASEDIR)

print scipp

rNo = 1
prjName = 'r%02dm.puf'%rNo

outFile = 'readpuf_temp.out'
if os.path.exists(outFile):
  os.remove(outFile) 
Inputs = (' %s%s %s%s %s%s%s %s%s'% ('RP',tail,'file TXT:'+ outFile,tail, 'go ',prjName,tail, 'exit', tail))
run_cmd.Command(env,scipp,Inputs,tail)
times = []
for line in fileinput.input(outFile):
  if fileinput.lineno() > 3:
    times.append(line.split()[0])


sigOutput = open('sigX.out',"w",0)
sigDat = []
for tval in times:
  os.remove(outFile) 
  Inputs = (' %s%s %s%s %s%8.3e%s %s%s %s%s%s %s%s'% ('RP',tail, 'file TXT:'+ outFile,tail, 'time ',float(tval),tail, 'var sxx si2',tail, \
            'go ',prjName,tail, 'exit', tail))
  run_cmd.Command(env,scipp,Inputs,tail)
  for line in fileinput.input(outFile):
    if fileinput.lineno() > 3:
      puffno,sigx,si2 = map(float,line.split()[0:3])
      puffno = int(puffno)
      sigx = np.sqrt(sigx)
      sigDat.append((float(tval),sigx,si2,puffno))
      sigOutput.write('%g %g %g %02d\n'%(float(tval), sigx, si2, puffno))
sigOutput.close()
sigDat = np.array(sigDat)

fig = plt.figure()
fig.hold()
plt.scatter(sigDat[:,1],sigDat[:,2],c=sigDat[:,0])

xmin = min(sigDat[:,1].min(),sigDat[:,2].min())
xmax = max(sigDat[:,1].max(),sigDat[:,2].max())
yp5 = np.array(([0.,0.],[xmax,xmax/2.]))
y1 = np.array(([0.,0.],[xmax,xmax]))
y2 = np.array(([0.,0.],[xmax,2.*xmax]))

plt.plot(yp5[:,0],yp5[:,1])
plt.plot(y1[:,0],y1[:,1])
plt.plot(y2[:,0],y2[:,1])
plt.xlabel('Sigmax')
plt.ylabel('Si2')
plt.xlim([0.,xmax])
plt.ylim([0.,xmax])
plt.colorbar(fraction=0.08)
plt.savefig('temp.png')
os.remove(outFile) 
#print sigDat
    

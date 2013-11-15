#
import os
import subprocess
import setSCIparams as SCI

baseDir = os.getcwd()
for tNo in range(18):
  #outDir = os.path.join(baseDir,'TRIAL%02d'%tNo)
  outDir = baseDir
  if os.path.exists(outDir):
    os.chdir(outDir)
    #prjName = 't%02d'%tNo
    prjName = 'r%02dm'%tNo
    if os.path.exists(prjName+'.log'):
      print outDir,prjName
      KeyNml = {'group_dose':'T'}
      myEnv = SCI.setEnv(binDir="/home/user/bnc/hpac/fromSCIPUFF/Repository/UNIX/FULL/bin/linux/lahey")
      SCI.runSci(prjName,myEnv=myEnv,KeyNml=KeyNml)
      addLog = ["/home/user/bnc/shl/add2log.pl","-l","%s.log"%prjName,"-s","%s.sam"%prjName]
      (output, errmsg) = subprocess.Popen(addLog,stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE).communicate()

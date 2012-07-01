#
import os
import sys
import subprocess

#
import run_cmd
import cmpPufDb
import cmpCols

if sys.platform == 'win32':
  #
  runDir              = "D:\hpac\\gitEPRI\\runs\\stepAmbwFlx"
  iniFile             = "D:\\hpac\\gitEPRI\\bin\\scipuff.ini"
  SCIPUFF_BASEDIR     = "D:\\hpac\\gitMain"
  compiler            = "intel"
  version             = "Release"
  hpacstub            = "HPACStub.exe"
  readpuf             = ["scipp.exe","-I:%s"%iniFile,"-R:RP"]
  #
  oldPath             = ".\\;C:\\Program Files (x86)\\Intel\\ComposerXE-2011\\redist\\ia32\\mpirt"
  vendorDir           = "%s\\bin\\vendor"%SCIPUFF_BASEDIR
  binDir              = "%s\\bin\\%s\\%s"%(SCIPUFF_BASEDIR,compiler,version)
  urbDir              = "%s\\bin\\%s\\urban\\%s"%(SCIPUFF_BASEDIR,compiler,version)
  nurDir              = "%s\\bin\\%s\\nonUrban\\%s"%(SCIPUFF_BASEDIR,compiler,version)
  os.environ["PATH"]  = "%s;%s;%s;%s;%s"%(vendorDir,binDir,urbDir,nurDir,oldPath)
  #
  tail = '\r\n'

env = os.environ.copy()
os.chdir(runDir)

for np in [1,4]:
  prjName = "x%d"%np
  cmd = ["mpiexec.exe","-n","%d"%np,"%s"%hpacstub]
  Inputs = ('%s%s %s%s'%(iniFile,tail,prjName,tail))
  print cmd
  print Inputs
  print env["PATH"]
  run_cmd.Command(env,cmd,Inputs,tail)
  cmpPufDb.createCSV(env,prjName,readpuf,tail)
cmpCols.cmpCol("x1.csv","x4.csv")


#!/bin/env python
import os
import sys
import socket

# Local lib files
import setSCIparams as SCI
import run_cmd

# Local files
import pltCmpAer

# Rewrite and plot the AerMet input files
    
def rdWrtInp(inpName,outName,addSCI):

  # read inpFile
  inpFile = open(inpName,'r')
  outFile = open(outName,'w')
  
  pNames    = ['CO','SO','RE','ME','OU']
  inSection = {}
  
  for line in inpFile:
    lStrip = line.strip()
    if len(lStrip) > 0:
      lData = lStrip.split('*')[0]
      if len(lData.strip()) == 0:
        outFile.write(line)
        continue
      if 'STARTING' in lData:
        sName = lData.strip().split()[0]
        if True in inSection:
          print 'Error in Starting. Already in section ',pNames[inSection.index(True)]
          sys.exit() 
        inSection.update({sName:True})
        print 'Starting section ',sName
        outFile.write(line)
        continue
      if 'FINISHED' in lData:
        sName = lData.strip().split()[0]
        if not inSection[sName]:
          print 'Error in Finished. Not in section ',sName
          sys.exit()
        if addSCI[sName] is not None:
          outFile.write('%s'%addSCI[sName])
        outFile.write(line)
        print 'Finished section ',sName        
        inSection.update({sName:False})
        if sName == 'CO':
          if addSCI['MA'] is not None:
            outFile.write('%s'%addSCI['MA'])
        continue
    outFile.write(line)
  inpFile.close()
  outFile.close()

def getMaxConc(prjName):
  sciConn,sciCur       = pltCmpAer.getSmpDb(prjName)
  (nTimes,nSmp,smpIds) = pltCmpAer.countSmpDb(sciCur)
  smpFac               = 1.e9
  for iHr in [1.]:
    sciArray = pltCmpAer.smpDbMax(sciCur,iHr,smpFac,smpIds=smpIds,nTimes=nTimes)
  
# Main program
if __name__ == '__main__':

  compName = socket.gethostname()
  env = os.environ.copy()
  
  # Local modules
  if  compName == 'pj-linux4':
    sys.path.append('/home/user/bnc/python')
    runDir = ''
  if compName == 'sm-bnc':
    #runDir = 'D:\\SCIPUFF\\EPRI\\runs\\kos_090811'
    #runDir = '/home/user/bnc/scipuff/runs/EPRI/wwright'
    runDir          = 'D:\\Aermod\\v12345\\runs\\kinsf6\\SCICHEM'
    SCIPUFF_BASEDIR = "D:\\SCIPUFF\\EPRI\\workspace\\EPRI\\bin\\intel\\Win32\\Release"
    INIfile         = "D:\\SCIPUFF\\EPRI\\Workspace\\EPRI\\scipuff.ini"
    
  runSCI  = os.path.join(SCIPUFF_BASEDIR,'runSCI')
  INIfile = "-I:" + INIfile
  runSCI  = [runSCI,INIfile,"-M:10000"]  
  
  os.chdir(runDir)
  
  # CO
  coStr = '   DELPRJFI NO\n   MAXTSTEP 900.\n   DOMAIN RECEPTORS METERS\n'
  coStr = coStr + '   OUTPTINT 3600\n'
  # MA
  maStr = '\nMA STARTING\n   MATCLASS SF6 Gas\n   DENSITY  SF6 1.2\n'
  maStr = maStr + '   GASDEPOS SF6 0.0\nMA FINISHED\n'
  # SO
  soStr = None
  # RE
  reStr = None
  # ME
  meStr = None
  # OU
  ouStr = None
  
  # Initialize addSCI
  addSCI = {'CO':coStr,'MA':maStr,'SO':soStr,'RE':reStr,'ME':meStr,'OU':ouStr}
    
  #inpName = raw_input('AERMOD inp file name? ')
  #inpName = 'KSF6-420.80I'
  for inpName in ['KSF6-424.80I']: #,'KSF6-425.80I','KSF6-427.80I','KSF6-428.80I','KSF6-430.80I']:
    inpFile = os.path.join(runDir,'..','AERMOD',inpName)
    prjName = inpName.replace('.','_')
    outName = prjName + '.aermod'
    rdWrtInp(inpFile,outName,addSCI)
    run_cmd.Command(env,runSCI,prjName+'\n','\n')
    getMaxConc(prjName)

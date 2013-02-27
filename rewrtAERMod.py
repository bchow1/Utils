
#!/bin/env python
import os
import sys
import socket
import numpy as np

# Local lib files
import setSCIparams as SCI
import run_cmd
import utilDb

# Local files
import pltCmpAer
import plotAerModDom

# Rewrite, run and plot AerMod type input files for SCICHEM 

def getSCIStr(aerInpFile,m2Km=None):

  # CO
  # get domain
  (sbl,sxy,rxy,latlon) = plotAerModDom.getAerDom(aerInpFile)
  xy = [[0.,0.] for i in range(4)] # [[xmin,xmax],[ymin,ymax],[xmean,ymean],[0.1dx,0.1dy]]
  (ix,iy) = (0,1)
  (iMin,iMax,iMen,iDif) = (0,1,2,3)
  for i in range(2):
    xy[i][iMin] = min(sxy[:,i].min(),rxy[:,i].min())*m2Km
    xy[i][iMax] = max(sxy[:,i].max(),rxy[:,i].max())*m2Km
    xy[iMen][i] = 0.5*(xy[i][iMin] + xy[i][iMax])
    xy[iDif][i] = 0.1*(xy[i][iMax] - xy[i][iMin])
    
  # CO
  pjnStr = '   PROJECTN CARTESIAN datum %6.2f %6.2f %6.2f %6.2f KM\n'%(latlon[1],latlon[0],xy[iMen][ix],xy[iMen][iy])
  domStr = '   DOMAIN %6.2f %6.2f '%(xy[ix][iMin]-xy[iDif][ix],xy[ix][iMax]+xy[iDif][ix])
  domStr = domStr + '%6.2f %6.2f %6.2f\n'%(xy[iy][iMin]-xy[iDif][iy],xy[iy][iMax]+xy[iDif][iy],4000.)
  coStr = '   DELPRJFI NO\n   MAXTSTEP 900.\n' #   DOMAIN RECEPTORS METERS\n'
  coStr = coStr + '   OUTPTINT 3600\n' + pjnStr + domStr 
  
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
  #ouStr = '   METOUTPT 3600. S\n   METFORMT ASCII\n'
  
  # Initialize addSCI
  addSCI = {'CO':coStr,'MA':maStr,'SO':soStr,'RE':reStr,'ME':meStr,'OU':ouStr}
  
  return addSCI
    
def rdWrtInp(inpName,outName,addSCI,m2Km=None):

  # read inpFile
  inpFile = open(inpName,'r')
  outFile = open(outName,'w')
  
  pNames    = ['CO','SO','RE','ME','OU']
  inSection = {'%s'%pName:False for pName in pNames }
  
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
        #print 'Starting section ',sName
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
        #print 'Finished section ',sName        
        inSection.update({sName:False})
        if sName == 'CO':
          if addSCI['MA'] is not None:
            outFile.write('%s'%addSCI['MA'])
        continue
      if m2Km is not None:
        if inSection['SO'] or inSection['RE']: 
          if sName == 'SO' and 'LOCATION' in lData:
            lsplit  = line.split()
            lsplit[-3] = str(float(lsplit[-3])*m2Km)  # x
            lsplit[-2] = str(float(lsplit[-2])*m2Km)  # y
            lsplit.extend('\n')
            line       = "  ".join(lsplit)          
          if sName == 'RE':
            if 'EVALCART' or 'DISCCART' in lData:
              lsplit  = line.split()
              indx = -1
              for indx in range(len(lsplit)):
                if lsplit[indx] == 'EVALCART'\
                  or lsplit[indx] == 'DISCCART':
                  break                          
              lsplit[indx+1] = str(float(lsplit[indx+1])*m2Km)  # x
              lsplit[indx+2] = str(float(lsplit[indx+2])*m2Km)  # y
              lsplit.extend('\n')
              line       = "  ".join(lsplit)
    outFile.write(line)
  inpFile.close()
  outFile.close()
  print 'Done creating ',outName
  return

def getMaxConc(prjName,iHr=1):
  sciConn,sciCur = pltCmpAer.getSmpDb(prjName)
  smpFac         = 1.e9  # kg/m3 to ug/m3
  sciArray       = pltCmpAer.smpDbMax(sciCur,iHr,smpFac)
  return sciArray
   
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
    runDir          = 'D:\\Aermod\\v12345\\runs\\kinso2\\SCICHEM'
    SCIPUFF_BASEDIR = "D:\\SCIPUFF\\EPRI\\workspace\\EPRI\\bin\\intel\\Win32\\Release"
    INIfile         = "D:\\SCIPUFF\\EPRI\\Workspace\\EPRI\\scipuff.ini"
    
  runSCI  = os.path.join(SCIPUFF_BASEDIR,'runSCI')
  INIfile = "-I:" + INIfile
  runSCI  = [runSCI,INIfile,"-M:10000"]  
  
  os.chdir(runDir)
  
  if 'kinsf6' in runDir.upper():
    units   = 'PPT'
    matName = 'SF6'
  else:
    units = 'ug/m3'
  
  if units == 'PPT' and matName == 'SF6':
    cFac = 167. # Convert from ug/m3 to ppt for SF6
  else:
    cFac = 1.
    
  #inpName = raw_input('AERMOD inp file name? ')
  inpNames = [] 
  for fName in os.listdir(os.path.join(runDir,'..','AERMOD')):
    if fName.endswith('I'):
      inpNames.append(fName)
      
  for inpName in ['KINSO2.INP']: #['KSF6-424.80I','KSF6-425.80I','KSF6-427.80I','KSF6-428.80I','KSF6-430.80I']:
    
    prjName = inpName.replace('.INP','').replace('.','_').lower()
    
    #
    # Get Observed concentration array
    #
    obsArray = pltCmpAer.getObsArray(prjName)*cFac   
    if len(obsArray) == 0:
      continue
    
    #
    # Create Aermod type input file for SCIPUFF
    #
    outName = prjName + '.aermod'
    os.chdir(os.path.join(runDir,'..','AERMOD'))
    aerDir = os.getcwd()
    os.chdir(runDir)
    inpFile = os.path.join(aerDir,inpName)
    m2Km = 1.e-3
    addSCI = getSCIStr(inpFile,m2Km=m2Km)
    #rdWrtInp(inpFile,outName,addSCI,m2Km=m2Km)
    
    #
    # Run SCICHEM
    #
    run_cmd.Command(env,runSCI,prjName+'\n','\n')
    
    #
    # Get maximum 1 hr avg SCIPUFF concentration
    #sciArray = getMaxConc('072480_new')*167. 
    sciArray = getMaxConc(prjName)*cFac
    
    #
    # AERMOD predicted concentration array
    #
    aerArray = pltCmpAer.getAerArray(prjName)*cFac
    
    #
    # Print top 10 values
    #
    for val in zip(obsArray[:10], aerArray[:10],sciArray[:10]):
      print '%5.1f %5.1f %5.1f'%(val[0],val[1],val[2])
     
    #
    # Q-Q plot
    # 
    pltCmpAer.plotData(obsArray, aerArray, sciArray, inpName + '.png', inpName, cutoff=0.0,units=units)
    
    print 'Done'
    

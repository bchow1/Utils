
#!/bin/env python
import os
import sys
import socket
import numpy as np

import measure

compName = socket.gethostname()

# Local modules
if compName == 'sm-bnc' or compName == 'sage-d600':
  sys.path.append('C:\\cygwin\\home\\sid\\python')
if  compName == 'pj-linux4':
  sys.path.append('/home/user/bnc/python')

# Main program
if __name__ == '__main__':

  if compName == 'sm-bnc':
    #runDir = 'd:\\scipuff\\EPRIx\\SCICHEM-2012\\runs\\tva\\tva_990715'
    #runDir = 'd:\\scipuff\\gitEPRI\\runs\\JAWMA_CMAS2012'
    runDir = 'D:\\TestSCICHEM\\Outputs\\loLSV_HiVOC\\Chemistry'
    
  if compName == 'pj-linux4':
    runDir = '/home/user/bnc/scipuff/EPRI_121001/runs/tva'
  if compName == 'sage-d600':
    runDir = 'D:\\SCICHEM-2012' 

  varNames = ['SO2','NOy'] 
    
  for prjName in ['tva_980825','tva_980826','tva_990706','tva_990715']:

    os.chdir(os.path.join(runDir,prjName+'\\SCICHEM'))
    ratOut = open('NSratio.txt','w')
    fList = os.listdir('.')
    for fName in fList:
      if fName.endswith('.npz'):
        if 'SO2' in fName:
          dist = fName.split('_')[0].replace('km','')

          #SO2
          npzfile = np.load(fName)
          so2Max_obs = npzfile['arr_0'].max()
          so2Max_pre = npzfile['arr_1'].max()
          print '\n',prjName,fName
          print 'SO2: ',so2Max_obs,so2Max_pre        
          #NOy
          fName = fName.replace('SO2','NOy')
          print fName
          npzfile = np.load(fName)
          noyMax_obs = npzfile['arr_0'].max()
          noyMax_pre = npzfile['arr_1'].max()
          print 'NO2: ',noyMax_obs,noyMax_pre
          ratOut.write('%s %8.3f %8.3f\n'%(dist, noyMax_obs/so2Max_obs, noyMax_pre/so2Max_pre))
    ratOut.close()      

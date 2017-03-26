#!/bin/python

import os
import subprocess

C1Areas = {'NE':['acad','grgu','prra'],'SE':['cohu','grsm2','joyc','mamo2','shro']}
binDir      = "/home/user/bnc/scipuff/Repository/export/EPRI/SCICHEM_3.0/SCICHEM_3.1_161013/bin/linux/ifort"
hdfDir      = "/home/user/sid/hdf5-1.8.7-linux-x86_64-shared/lib"
iniFile     = "../../../scipuff.ini"
env         = os.environ.copy()
env["LD_LIBRARY_PATH"] = "%s:%s" % (binDir,hdfDir)
sciPost     = [os.path.join(binDir,'sciDOSpost'),'-I:%s'%iniFile,'-i']

def runSCIPost(region):
  cwd = os.getcwd()
  os.chdir('/home/user/bnc/scipuff/runs/EPRI/ModelComp/%s/tavg1_newAmb'%region)

  # Create sciDOSPost input file
  for C1Area in C1Areas[region]:
    recFile = 'Class1Area/%s-recep.dat'%C1Area
    flagName = C1Area.replace('2','')
    if not os.path.exists(recFile):
      print 'Error: Cannnot find %s'%recFile
      continue
    scipo_out = open('scipo_%s.output'%C1Area,'w')
    scipo_err = open('scipo_%s.error'%C1Area,'w')

    mcFile = 'max_concentrations.%s.csv'%C1Area
    vrFile = 'visibility_results.%s.csv'%C1Area
    o3File = 'o3.DV.%s.xyz'%C1Area
    pso4File = 'pso4.DV.%s.xyz'%C1Area
    pno3File = 'pno3.DV.%s.xyz'%C1Area
    visFile = 'visibility.DV.%s.xyz'%C1Area
    #
    inpFile = 'sciDOSpost_%s_%s.inp'%(region,C1Area)
    oFile = open(inpFile,'w')
    oFile.write('Project modelcomp_%s_ann\n'%region.lower())
    oFile.write('calculate plume\n')
    oFile.write('Start 2011010101\n')
    oFile.write('stop  2011123124\n')
    oFile.write('REC 1  %s   LATLON  %s\n'%(flagName,recFile))
    oFile.write('con  o3    max  4th   8 hr max_in 24 hr CSV   %s\n'%mcFile)
    oFile.write('con  pso4  max  1st  24 hr avg_in 24 hr CSV   %s\n'%mcFile)
    oFile.write('con  pso4  max  1st   8759 hr avg_in 8759 hr CSV   %s\n'%mcFile)
    oFile.write('con  pno3  max  1st  24 hr avg_in 24 hr CSV   %s\n'%mcFile)
    oFile.write('con  pno3  max  1st   8759 hr avg_in 8759 hr CSV   %s\n'%mcFile)
    oFile.write('vis  dBext max  8th  24 hr avg_in 24 hr CSV   %s\n'%vrFile)
    oFile.write('con  o3    >-1  1st   8 hr max_in 24 hr XYZ   %s\n'%o3File)
    oFile.write('con  pso4  >-1  1st  24 hr avg_in 24 hr XYZ   %s\n'%pso4File)
    oFile.write('con  pno3  >-1  1st  24 hr avg_in 24 hr XYZ   %s\n'%pno3File)
    oFile.write('vis  dBext >-1  1st  24 hr avg_in 24 hr CSV   %s\n'%visFile)
    oFile.close()
    print 'In ',os.getcwd()
    cmd = sciPost + [inpFile]
    print '  CMD = ',cmd
    h = subprocess.Popen(cmd, env=env, bufsize=0, shell=False,stdout=scipo_out,stderr=scipo_err)
    h.communicate()
    scipo_out.close()
    scipo_err.close()
  os.chdir(cwd)  
  
for region in ['NE','SE']:
  runSCIPost(region)

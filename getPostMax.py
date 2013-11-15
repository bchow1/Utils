#
import os
import sys
import numpy as np

import run_cmd

if sys.platform == 'win32':
  smp2post = 'smp2post' 
else:
  smp2post = '/home/user/bnc/scipuff/Repository/export/EPRI/EPRI_130620/bin/linux/ifort/smp2post'
if sys.argv.__len__() > 1:
  for i in range(1, sys.argv.__len__()):
    pstFile = sys.argv[i]
    if not os.path.exists(pstFile):
      smpFile = pstFile.replace('.pst','') 
      smpFile = smpFile.replace('.post','')
      cmd = [smp2post,'-i',smpFile,'-o',pstFile] 
      run_cmd.Command(None,cmd,'',None)
    postArray = np.loadtxt(pstFile,skiprows=8,usecols=[0,1,2,8],dtype={'names':('x','y','cmean','ymdh'),\
                                                                'formats':('float','float','float','S8')})
    concRanked = np.sort(postArray,order='cmean')[::-1]
    print
    print pstFile,": "
    for i in range(10):
      cVal = concRanked[i]
      print i,cVal['cmean'],cVal['ymdh'],cVal['x'],cVal['y']
    print

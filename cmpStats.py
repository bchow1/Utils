#
import sys
import os
import numpy as np

def writeStats(cmpOut,obsData,preData,colNames,head=False,tail='\n'):

  nObs = obsData.shape[1]
  print 'nObs = ',nObs

  if head:
    cmpOut.write('----------------------------------------------------------%s'%tail)
    cmpOut.write('            FB    NMSE    MG    VG     FAC2  FAC5   FACBar%s'%tail)
    cmpOut.write('----------------------------------------------------------%s'%tail)
    #cmpOut.write('-------------------------------------------------%s'%tail)
    #cmpOut.write('            FB    NMSE    MG    VG     FAC2  FAC5%s'%tail)
    #cmpOut.write('-------------------------------------------------%s'%tail)

  for ncol in range(len(colNames)):
    #
    obs  = obsData[ncol,:]
    obsAvg = np.mean(obs)
    #
    pre = preData[ncol,:]
    preAvg = np.mean(pre)
    #
    FB = 2.*(obsAvg-preAvg)/(obsAvg+preAvg)
    NMSE = np.mean((obs-pre)**2)/(obsAvg*preAvg)
    if ncol == 5:
      sd = 0.
      for i in range(len(obs)):
        sd += np.log(obs[i]) - np.log(pre[i])
        print '%7.2f %7.2f %7.2f %7.2f %7.2f %7.2f'%(obs[i],pre[i],np.log(obs[i]),np.log(pre[i]),np.log(obs[i]) - np.log(pre[i])-0.16,sd)
      print '%7.2f %7.2f'%(sd/float(len(obs)),np.exp(sd/float(len(obs))))
      gom = np.mean(np.log(obs))
      gpm = np.mean(np.log(pre))
      print '%7.2f %7.2f %7.2f'%(gom,gpm,np.exp(gom-gpm))
    MG = np.exp(np.mean(np.log(obs) - np.log(pre)))
    VG = np.exp(np.mean((np.log(obs) - np.log(pre))**2))
    fac2 = -999.
    fac5 = -999.
    #
    fac = pre/obs
    #print fac
    if "/" in colNames[ncol]:
      facbar = np.mean(fac)
    else:
      for rat in [2.,5.]:
        mask = (fac>=1/rat) & (fac<=rat)
        facMask = fac[mask]
        #print rat,len(facMask),mask
        if rat == 2.:
          fac2 = len(facMask)/float(nObs)
        else:
          fac5 = len(facMask)/float(nObs)
    if "/" in colNames[ncol]:
      cmpOut.write( '%6s   %6.3f %6.3f %6.3f %6.3f %6s %6s %6.3f%s'%(colNames[ncol],FB,NMSE,MG,VG,'-','-',facbar,tail))
    else:
      #cmpOut.write( '%6s   %6.3f %6.3f %6.3f %6.3f %6.3f %6.3f %6s%s'%(colNames[ncol],FB,NMSE,MG,VG,fac2,fac5,'-',tail))
      cmpOut.write( '%6s   %6.3f %6.3f %6.3f %6.3f %6.3f %6.3f %s'%(colNames[ncol],FB,NMSE,MG,VG,fac2,fac5,tail))
  if head:
    cmpOut.write('----------------------------------------------------------%s'%tail)
  cmpOut.close()
  return

if __name__ == '__main__':

  colNames = ['DMAX']
  obsData = np.zeros([1,3])
  obsData[0,:] = np.array([0.82818715809, 1.0, 0.359178700303])
  preData = np.zeros([1,3])
  preData[0,:] = np.array([0.917759595661, 0.602523815506, 0.253088519684])
  #print obsData.shape,preData.shape
  cmpOut = open('stats.out','w',0)
  writeStats(cmpOut,obsData,preData,colNames,tail='\n')
  cmpOut.close()


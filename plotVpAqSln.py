#
import os
import sys
import numpy as np
import scipy.optimize.minpack as soptmp
import matplotlib.pyplot as plt

# Local libs
import utilPlot

def rdVpTable(fName):
  vpFile = open(fName,'r')
  nTp = -1
  Cmpnt1 = None
  Cmpnt2 = None
  for line in vpFile:
    if len(line.strip()) == 0 or len(line.replace(",","")) <= 1:
      continue
    if line.startswith('#Deg C'):
      if Cmpnt1 is None:
        Cmpnt1 = []
      else:
        Cmpnt2 = []
        nTp = -1
      continue
    if line.startswith('#'):
      continue
    if nTp < 0:
      tpList = line.split(',')
      nTp = tpList.index('')
      tpList = tpList[:nTp]
      # Add dummy number for temperature column
      tpList.insert(0,'-9999')
      if Cmpnt2 is None:
        Cmpnt1.append(tpList)
      else:
        Cmpnt2.append(tpList)      
      #print tpList
    else:
      vpList = line.split(',')[:nTp+1]
      #print vpList
      if Cmpnt2 is None:
        Cmpnt1.append(vpList)
      else:
        Cmpnt2.append(vpList)
  Cmpnt1 = np.array(Cmpnt1,dtype=float)
  Cmpnt2 = np.array(Cmpnt2,dtype=float)
  #print Cmpnt1,'\n'
  #print Cmpnt2,'\n'
  return Cmpnt1,Cmpnt2

def residual(p,y,T):
  A,B,C = p
  ant_vp_calc = A - B/(T+C)
  err = y - ant_vp_calc
  return err

def ant_vp_eval(T,p):
  A,B,C = p
  vp = 10**(A - B/(T+C))
  return vp
  
def calcAntCoeff(csvFile):
  p0 = [10.0,2000.0,273.15]
  Cmpnt1,Cmpnt2 = rdVpTable(csvFile)
  for iCmp,Cmpnt in enumerate([Cmpnt1,Cmpnt2]):
    if iCmp == 0:
      cmpName = 'HNO3'
    else:
      cmpName = 'H2O'
    pltList = []
    Tp = Cmpnt[1:,0]
    Pct = Cmpnt[0,1:]
    #print 'T = ',Tp
    #print '% = ',Pct
    print '\n'
    for nPc,Pc in enumerate(Pct):
      vP = Cmpnt[1:,nPc+1]
      #print '\nFor %',Pc
      T  = Tp[vP > 0.]
      vp_flt = vP[vP > 0.]
      log_vp = np.log10(vp_flt)
      #print T,vp_flt
      plsq = soptmp.leastsq(residual,p0,args=(log_vp,T))
      #print 'Antoine Coefficients'
      A,B,C = plsq[0]
      print '%s %4.2f %7.2f %6.2f'%(Pc,A,B,C)
      plt.figure()
      plt.clf()
      plt.plot(T,vp_flt,'o')
      plt.plot(T,ant_vp_eval(T,plsq[0]),'r-')
      #plt.legend(['Vapor Pressure(mm)','Antoine data fit(%4.2f %7.2f %6.2f)'%(A,B,C)],'best' )
      plt.legend(['Data','Antoine fit'],'best' )
      plt.title('Vap. Pr(mm Hg) for %5.1f %% solution for %s'%(Pc,cmpName))
      pltName = cmpName+'_%05.1f'%Pc+'.pdf'
      plt.savefig(pltName)
      #plt.show()
    utilPlot.joinPDF(pltList,cmpName+'.pdf')


# Call main program
if __name__ == '__main__':
  os.chdir('D:\\ABS\\HNO3_H20')
  
  calcAntCoeff('HNO3SlnVP.csv')
  sys.exit()
  
  aCoeff = np.loadtxt('AntoineHCLSoln.csv',skiprows=2,delimiter=',')
  #np.loadtxt
  #print aCoeff
  #pct = np.array([i for i in range(2,43)])
  pct = np.array([2,10,20,30,40,50,70,80,90,100])
  coeffA = np.interp(pct,aCoeff[:,0],aCoeff[:,1])
  coeffB = np.interp(pct,aCoeff[:,0],aCoeff[:,2])
  coeffC = np.interp(pct,aCoeff[:,0],aCoeff[:,3])
  #print coeffA,coeffB,coeffC
  plt.hold(True)
  for ta in range(0,51,2): 
    cp = []
    for ip,pr in enumerate(pct):
      press = 10**(coeffA[ip] - coeffB[ip]/(ta+coeffC[ip]))
      cp.append([pr,press])
    cp = np.array(cp)
    #print pr,coeffA[ip],coeffB[ip],coeffC[ip]
    #plt.clf()
    plt.semilogy(cp[:,0],cp[:,1])
  plt.title('Temp from 0 to 50 (C)')
  plt.xlabel('HCL percent')
  plt.ylabel('P(mm)')
  plt.hold(False)
  plt.savefig('Temp.png')
  
    
       
 
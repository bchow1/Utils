#
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Call main program
if __name__ == '__main__':
  os.chdir('D:\\ABS')
  aCoeff = np.loadtxt('AntoineHCLSoln.csv',skiprows=2,delimiter=',')
  #np.loadtxt
  #print aCoeff
  pct = np.array([i for i in range(2,43)])
  coeffA = np.interp(pct,aCoeff[:,0],aCoeff[:,1])
  coeffB = np.interp(pct,aCoeff[:,0],aCoeff[:,2])
  coeffC = np.interp(pct,aCoeff[:,0],aCoeff[:,3])
  #print coeffA,coeffB,coeffC
  
  for ta in range(0,51,2): 
    cp = []
    for ip,pr in enumerate(pct):
      press = 10**(coeffA[ip] - coeffB[ip]/(ta+coeffC[ip]))
      cp.append([pr,press])
    cp = np.array(cp)
    #print pr,coeffA[ip],coeffB[ip],coeffC[ip]
    plt.clf()
    plt.hold(True)
    plt.semilogy(cp[:,0],cp[:,1])
    plt.title('Temp = %d(C)'%ta)
    plt.xlabel('HCL percent')
    plt.ylabel('P(mm)')
    plt.hold(False)
    plt.savefig('Temp%d.png'%ta)
    
    
       
 
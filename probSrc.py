# PrbSrc module
from numpy import *

def clnpar(rat,gbar,sigg): # Determines the Gaussian mean and sigma 
  
  ratArr = array([
    [ 0.1000000    ,   1.000000    ,  0.9999996E-01 ],
    [ 0.1500000    ,   1.000000    ,  0.1500000 ],
    [ 0.2000000    ,   1.000000    ,  0.2000000 ],
    [ 0.2500000    ,  0.9999981    ,  0.2500072 ],
    [ 0.3000000    ,  0.9999660    ,  0.3001260 ],
    [ 0.3500000    ,  0.9997762    ,  0.3507082 ],
    [ 0.4000000    ,  0.9991474    ,  0.4023888 ],
    [ 0.4500000    ,  0.9976677    ,  0.4558905 ],
    [ 0.5000001    ,  0.9948961    ,  0.5118033 ],
    [ 0.5500001    ,  0.9904375    ,  0.5705312 ],
    [ 0.6000001    ,  0.9835079    ,  0.6329482 ],
    [ 0.6500001    ,  0.9738972    ,  0.6989896 ],
    [ 0.7000001    ,  0.9609293    ,  0.7692201 ],
    [ 0.7500001    ,  0.9440483    ,  0.8439555 ],
    [ 0.8000001    ,  0.9230663    ,  0.9231166 ],
    [ 0.8500001    ,  0.8968502    ,   1.007575 ],
    [ 0.9000002    ,  0.8654099    ,   1.097018 ],
    [ 0.9500002    ,  0.8281893    ,   1.191711 ],
    [ 1.000000    ,  0.7846111    ,   1.291921  ],
    [ 1.999999    ,  -2.051569    ,   4.630424 ],
    [ 2.499999    ,  -5.387887    ,   7.371889 ],
    [ 2.999999    ,  -10.33678    ,   10.89142 ],
    [ 3.499999    ,  -17.10986    ,   15.23050 ],
    [ 3.999999    ,  -25.86062    ,   20.41066 ],
    [ 4.500000    ,  -36.68866    ,   26.43834 ],
    [ 5.000000    ,  -49.73885    ,   33.34196 ],
    [ 5.500000    ,  -65.23964    ,   41.18114 ],
    [ 6.000000    ,  -83.07764    ,   49.88799 ],
    [ 6.500000    ,  -102.7420    ,   59.26623 ],
    [ 7.000000    ,  -126.4875    ,   70.10172 ],
    [ 7.500000    ,  -150.7448    ,   81.11997 ],
    [ 8.000000    ,  -180.4022    ,   94.00233 ],
    [ 8.500000    ,  -210.8741    ,   107.1658 ],
    [ 9.000000    ,  -243.3536    ,   120.9987 ],
    [ 9.500000    ,  -282.4449    ,   137.0364 ],
    [ 10.00000    ,  -321.5363    ,   153.0740 ],
    [ 15.00000    ,  -889.7404    ,   369.6515 ],
    [ 20.00000    ,  -1775.106    ,   682.2498 ],
    [ 25.00000    ,  -3045.141    ,   1105.600 ],
    [ 30.00000    ,  -4594.355    ,   1606.689 ],
    [ 35.00000    ,  -6666.756    ,   2250.804 ],
    [ 40.00000    ,  -8739.157    ,   2894.920 ],
    [ 45.00000    ,  -11847.44    ,   3809.671 ],
    [ 50.00000    ,  -15083.71    ,   4757.863 ],
    [ 55.00000    ,  -18319.99    ,   5706.056 ],
    [ 60.00000    ,  -21556.27    ,   6654.248 ],
    [ 65.00000    ,  -26853.44    ,   8116.241 ],
    [ 70.00000    ,  -32176.01    ,   9584.565 ],
    [ 75.00000    ,  -37498.57    ,   11052.89 ],
    [ 80.00000    ,  -42821.14    ,   12521.21 ],
    [ 85.00000    ,  -48143.71    ,   13989.54 ],
    [ 90.00000    ,  -53466.27    ,   15457.86 ],
    [ 95.00000    ,  -59305.60    ,   17048.81 ],
    [ 100.0000    ,  -68524.72    ,   19441.78 ]
    ], dtype = float, order='Fortran')

  ratIndx = array(ratArr[:,0],dtype=float, order='Fortran') 
  i = ratIndx.searchsorted(rat) - 1 

  # Values of rat less than 0.1 - These values are outside of the table
  if rat < 0.1:
    gbar = 1.0
    sigg = rat
    clnpar = [gbar, sigg]
    return clnpar
  # Values of rat > 100. - These values are outside of the table
  elif rat > 100. :
    i = i-1
 
  drat = ratArr[i+1,0] - ratArr[i,0]
  
  beta = (rat - ratArr[i,0]) / drat
  betm = 1. - beta
  
  gbar = betm*ratArr[i,1] + beta*ratArr[i+1,1] 
  sigg = betm*ratArr[i,2] + beta*ratArr[i+1,2]
  clnpar = [gbar, sigg]

  return clnpar 
 
def prbGtC(cbar,csig,cmin):

  import scipy
  import scipy.special

  rat  = max(.001,csig/cbar)
  gbar = 1
  sigg = 1
  [gbar, sigg] = clnpar(rat,gbar,sigg)
  arg = (cmin/cbar - gbar)/sigg
  if arg > 5. :
    pgtc = 0.
  elif arg < -5. :
    pgtc = 1.
  else :
    pgtc = 0.5*scipy.special.erfc( arg/sqrt(2.) )

  return pgtc 

# Main program for testing

if __name__ == '__main__':
  cbar = 1.
  cmin = 0.
  for csig in [1e-10]: # [ 1e-10,.001,1., 1.35,.65,1.,1.94,1.999999,7.5,10.1,55.6,100.3,1e+10]:
    print csig
    print prbGtC(cbar,csig,cmin)
    print


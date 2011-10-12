#
import os
import sys
import fileinput

import convertUTM

def km2m(x):
  x = float(x)*1000.
  return x 

myConvertUTM = convertUTM.convertUTM()
myConvertUTM.utmz = 12

for line in fileinput.input(sys.argv[1]):
  if fileinput.lineno() > 1:
    samList = line.strip().split()
    myConvertUTM.x,myConvertUTM.y = map(km2m,samList[:2])
    myConvertUTM.UTMtoGeog()
    print fileinput.lineno()-1,myConvertUTM.x*1e-3,myConvertUTM.y*1e-3,myConvertUTM.latd,myConvertUTM.lngd    
fileinput.close()

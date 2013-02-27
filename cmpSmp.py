#
import os
import numpy as np
import matplotlib.pyplot as plt

def combineSmps():
# Combines multiple smp files into a single npy
# Hard coded for 3 variables only.
  fList = os.listdir('./')
  smpList = []
  for fName in fList:
    if fName.endswith('.smp'):
      smpList.append(fName)
  print len(smpList),smpList
  
  smpConc = []
  for ns,smp in enumerate(smpList):
    smpFile = open(smp,'r')
    for line in smpFile:
      nVar = (int(line.strip())-1)/3
      break
    smpFile.close()
    colList  = [i for i in range(1,nVar*3+1,3)]
    print smp,colList
    if nVar < 4:
      skipRows = 3
    else:
      skipRows = 4
  
    conc = np.loadtxt(smp,skiprows=skipRows,usecols=colList)
    smpConc.extend(list(np.reshape(conc,np.size(conc))))
  
  smpConc = np.array(smpConc)
  smpConc = np.sort(smpConc)[::-1]
  np.size(smpConc)
  np.save('smpConc.npy',smpConc)


# Main program to compare 2 smp files. The column names and numbers must be set
if __name__ == '__main__':
  
  # Set filenames and columns
  os.chdir('d:\\SCIPUFF\\EPRI\\runs\\tva\\tva_990715')
  useCols =  (0,4,5,6)
  dType   = {'names':('t','no2','no','o3'),'formats':('float','float','float','float')}
  pFile1  = 'negO3_1min_step'
  pFile2  = 'negO3_1sec_step'
  figName = 'negO3_diff_1min_1sec.png'
  #
  c1 = np.loadtxt(pFile1 + '.smp',skiprows=1,usecols=useCols,dtype=dType)
  c2 = np.loadtxt(pFile2 + '.smp',skiprows=1,usecols=useCols,dtype=dType)
  #
  plt.hold(True)
  h1, = plt.plot(c1['t'],c1['o3'],color='green',marker='+',markerfacecolor='green')
  h2, = plt.plot(c2['t'],c2['o3'],color='blue',marker='x',markerfacecolor='blue')
  plt.xlabel('Time(sec)')
  plt.ylabel('O3 conc(ppm)')
  plt.xlim(0,70)
  plt.legend([h1,h2],[pFile1,pFile2],bbox_to_anchor=(0.45,0.2))
  plt.hold(False)
  plt.savefig(figName)

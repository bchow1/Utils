#
import os
import numpy as np
import matplotlib.pyplot as plt

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

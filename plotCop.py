
#
import os
import sys
import socket
import fileinput
import math
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import measure

compName = socket.gethostname()

# Local modules
if  compName == 'pj-linux4':
  sys.path.append('/home/user/bnc/python')

def readcOP(fileName, run):
  cOP   = []
  arcOP = [[] for i in range(3)]
  for line in fileinput.input(fileName):
    if line.startswith('time'):    
      arc1 = line.split()[3:5]
      arc2 = line.split()[5:7]
      arc3 = line.split()[7:9]
      print arc1, arc2, arc3
      arcOP[0].append(map(float,arc1))
      arcOP[1].append(map(float,arc2))
      arcOP[2].append(map(float,arc3))
      cOP.append(map(float,arc1))
      cOP.append(map(float,arc2))
      cOP.append(map(float,arc3))
  cOP = getMaskedArray(cOP)
  arcOP = np.array(arcOP)
  print arcOP.shape
  print run
  
  plt.hold(True)
  for arc in range(3):
    getStats(arcOP[arc,:,1], arcOP[arc,:,0], statFile, run ,str(arc))
  #print cOP  #

  return (cOP,arcOP)

def getMaskedArray(cOP):
    cOP = np.array(cOP)
    cOP[:,0] = np.sort(cOP[:,0])
    cOP[:,1] = np.sort(cOP[:,1])
    cOP = ma.masked_where(cOP<-98.0,cOP)*1e-3
    print cOP
    return cOP

def getStats(data1, data2, statFile, case, arc):
  global skew, std, obs
  
  #upa = measure.upa(data1, data2)
  obsMean =  np.mean(data2)
  predMean = np.mean(data1)
  nmse = measure.nmse_1(data1, data2, cutoff=0.0)
  nmb  = measure.nmb(data1,data2)
  #fac2 = measure.fac2(data1, data2)
  #mfbe = measure.mfbe(data1, data2, cutoff=0.0)
  #mbe = measure.mbe(data1,data2, cutoff=0.0)
  #biasFac = measure.bf(data1,data2, cutoff=0.0)
  correlation = measure.correlation(data1,data2, cutoff=0.0 ) 
  if case == 'Skew':
    if arc == '0':
      skew = []
    skew.append(data1)
  if case == 'Standard':
    if arc == '0':
      obs = []
      std = []
    std.append(data1)
    obs.append(data2)
    if arc == '2':
      #plt.hold(True)
      for i in range(3):
        data2 = obs[i]
        data1 = std[i]
        data3 = skew[i]
        data1 = data1[data2 > 0.]
        data3 = data3[data2 > 0.]
        data2 = data2[data2 > 0.]
        print data1
        print data2
        print data3
        diff1 = data1 - data1.mean()
        diff2 = data2 - data2.mean()
        diff3 = data3 - data3.mean()
        print i,diff1,diff2,diff3
        plt.scatter(diff2,diff1,color='red')
        plt.scatter(diff2,diff3,color='green')
        #plt.show()
      #plt.hold(False)
      #plt.show() 
          
  print 'getStats:'
  print 'obs =',data2
  print 'pre =',data1
  print 'Case,arc,stats: ',case,arc,obsMean, predMean, nmse, nmb, correlation
  if statFile is not None:
    #statFile.write("%s,%s,%8.3f, %8.3f, %8.3f, %8.3f\n"%(case, arc, upa, nmse, mfbe,fac2))
    statFile.write("%8.2f, %8.2f, %8.2f, %8.2f,%8.2f\n"%(obsMean, predMean, nmse, nmb, correlation))    

if compName == 'sage-d600':
  runDir = 'D:\\SCICHEM-2012\\Cop'
if compName == 'sm-bnc':
  runDir = 'D:\\SCIPUFF\\runs\\EPRI\\COP'
  
os.chdir(runDir)

params1 = {'axes.labelsize': 8, 'text.fontsize':8 , 'xtick.labelsize': 8,
           'ytick.labelsize': 8, 'legend.pad': 0.1,  # empty space around the legend box
           'legend.fontsize': 8, 'lines.markersize': 6, 'lines.width': 2.0,
           'font.size': 10}

plt.rcParams.update(params1)

def pltWPDF():
  #Skewed vetical velocity pdf based on Luhar, et al (1996) for various
  # values of skewness S
  
  sVals = [0.0,0.3,0.6]
  wVals = [ -5.+ float(i)*0.1 for i in range(100) ] # w/w*
    
  plt.clf()
  plt.hold(True)
  lH = []
  lT = []
  
  #sigw/w* is a function of z/Zi
  z = 0.5
  sigw = math.sqrt(1.1*(1.05-z)*z**(2./3.))
  mark = ['o','s','d']
  
  for i,S in enumerate(sVals):
    pdf = np.zeros(len(wVals))
    if S == 0.:
      for j,w in enumerate(wVals):
        pdf[j] = 1./(math.sqrt(2.*math.pi)*sigw) * math.exp(-0.5*w**2/sigw**2)
    else:
      m = (2./3.)*S**(1./3.)
      r = ((1. + m**2)**3*S**2)/((3.+m**2)**2*m**2)
      L2 = 0.5*(1-math.sqrt(r/(4.+r)))
      L1 = 1.-L2
      
      sigw1 = sigw*math.sqrt(L2/(L1*(1.+m**2)))
      sigw2 = sigw*math.sqrt(L1/(L2*(1.+m**2)))
      w1    = -m*sigw1
      w2    =  m*sigw2
      
      for j,w in enumerate(wVals):
        pdf[j] = L1/(math.sqrt(2.*math.pi)*sigw1) * math.exp(-0.5*(w-w1)**2/sigw1**2) + \
                  L2/(math.sqrt(2.*math.pi)*sigw2) * math.exp(-0.5*(w-w2)**2/sigw2**2)
    lh, = plt.plot(wVals,pdf,color='black',marker=mark[i])            
    lH.append(lh)
    lT.append(r'$S$=%2.1f'%S)
  
  w0 = np.array([[0.,0.],[0.,1.]])
  plt.plot(w0[:,0],w0[:,1],color='black')
  plt.xlim([-1.5,1.5])
  plt.ylim([0.,1.])
  #plt.xlabel(r'$w/w_*$')
  plt.text(-0.1,-0.06,r'$w/w_*$',fontsize=10)
  #plt.ylabel(r'P($w$)')
  plt.text(-1.7,0.6,r'P($w$)',rotation='vertical',fontsize=10)
  #plt.title(r'$w-PDF$ as function of $S$',fontsize=10)
  figCaption1 = r'Figure 1:  The Probability Density Function of $w$ as function of Skewness'
  plt.text(-1.5,-0.1,figCaption1,fontsize=10)#transform=ax.transAxes,
  plt.legend(lH,lT)
  plt.hold(False)
  #plt.show()
  plt.savefig('w-pdf.eps',dpi=300)
  print "Done plotting w-pdf"
   
#pltWPDF()


statFile = open("COP_stat.csv","w")
statFile.write("Case, Arc, upa, nmse_1, mfbe, fac2\n")

fileName = os.path.join(runDir,'cop.all')
cSkewOP,arcSkewOP  = readcOP(fileName, "Skew")
#print 'cSkewOP',cSkewOP
#print 'arcSkewOP',arcSkewOP

fileName = os.path.join(runDir,'SCICHEM-01','cop.all')
cStdOP,arcStdOP   = readcOP(fileName, "Standard")
'''
print 'cStdOP',cStdOP
print 'arcStdOP',arcStdOP

fig = plt.figure()
plt.clf()
fig.subplots_adjust(bottom=0.2)
ax = fig.add_subplot(111)
plt.hold(True)

hskew = plt.scatter(cSkewOP[:,0],cSkewOP[:,1],color='black',marker='o',s=30)
hstd  = plt.scatter(cStdOP[:,0],cStdOP[:,1],color='black',marker='^',s=30)

vmin = 0.
vmax = max(cSkewOP.max(),cStdOP.max())
print vmin,vmax
plt.xlim([vmin,vmax])
plt.ylim([vmin,vmax])
#plt.title('Comparison of Maximum Concentration', fontsize=10)
plt.plot([vmin,vmax],[vmin,vmax],'k-')
#plt.plot([vmin,vmax],[vmin*0.5,vmax*0.5],'r-')
#plt.plot([vmin,vmax],[vmin*2,vmax*2],'r-')
plt.xlabel(r'Observed ($\mu g/m^3$)', fontsize=10)
plt.ylabel(r'Predicted ($\mu g/m^3$)', fontsize = 10)
figCaption = 'Figure 2:  Quantile-Quantile plot of concentration for Copenhagen data'
plt.text(-0.01,-1.3,figCaption,fontsize=10)
plt.legend([hskew,hstd],['Skewed Model','Standard Model'],bbox_to_anchor=(0.25,0.97))
plt.hold(False)
#plt.show()
plt.savefig('cop_ord.eps', dpi=300)
print 'Done plotting in ',os.getcwd()
'''
#clr = ['1.0','0.75','0.5']
#clr = ['red','blue','green']
cMx = [[.5,8.],[0.,4.],[0.,3.]]

for arc in range(3):
  
  stdCo = arcStdOP[arc,:,0]
  stdCp = arcStdOP[arc,:,1]
  stdCp = np.sort(stdCp[stdCo > 0.])*1e-3
  stdCo = np.sort(stdCo[stdCo > 0.])*1e-3
  
  skewCo = arcSkewOP[arc,:,0]
  skewCp = arcSkewOP[arc,:,1]
  skewCp = np.sort(skewCp[skewCo > 0.])*1e-3
  skewCo = np.sort(skewCo[skewCo > 0.])*1e-3
  
  print 'Arc = ',arc,skewCo[0],skewCp[0],stdCo[0],stdCp[0]
  #print 'std'
  #for i in range(len(stdCo)):
  #  print i,stdCo[i],stdCp[i]
  #print 'skew'
  #for i in range(len(skewCp)):
  #  print i,skewCo[i],skewCp[i]
  
  fig = plt.figure()
  plt.clf()
  plt.hold(True)
  
  hskew = plt.scatter(skewCo,skewCp,color='k',marker='o',s=30)
  hstd  = plt.scatter(stdCo,stdCp,color='k',marker='^',s=30)
  
  vmin = cMx[arc][0]
  vmax = cMx[arc][1]
  
  plt.xlim([vmin,vmax])
  plt.ylim([vmin,vmax])
  plt.plot([vmin,vmax],[vmin,vmax],'k-')
  plt.xlabel(r'Observed ($\mu g/m^3$)', fontsize=10)
  plt.ylabel(r'Predicted ($\mu g/m^3$)', fontsize = 10)
  plt.legend([hskew,hstd],['Skewed Model','Standard Model'],bbox_to_anchor=(0.25,0.97))
  
  plt.hold(False)
  plt.savefig('cop_ord_arc%d.png'%arc)
  
print 'Done plotting in ',os.getcwd()


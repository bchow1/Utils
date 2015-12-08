
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

isColor = True
zoL = [43.0,5.0,10.4,2.3,1.4,2.3,13.6,11.3,5.5]
pgtbc = 'green' #0.5'
pgtc  = 'blue' #'0.25'
pgtd = 'red' #0.0'
#pgt = [pgtc,pgtc,pgtc,pgtc,pgtc,pgtd,pgtbc,pgtbc,pgtd]
#pgt = ['red','blue','red','green','green','green','red','red','blue']
pgt = ['0.0','0.5','0.0','1.0','1.0','1.0','0.0','0.0','0.5']

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
  
  #plt.hold(True)
  for arc in range(3):
    getStats(arcOP[arc,:,1], arcOP[arc,:,0], statFile, run ,str(arc))
  #print cOP  #

  return (cOP,arcOP)

def getMaskedArray(cOP):
    cOP = np.array(cOP)
    cOP[:,0] = np.sort(cOP[:,0])
    cOP[:,1] = np.sort(cOP[:,1])
    cOP = ma.masked_where(cOP<-98.0,cOP)*1e-3
    print 'Sorted cOP = ',cOP
    return cOP

def getStats(data1, data2, statFile, case, arc):
  global skew, std, obs
  
  #upa = measure.upa(data1, data2)
  obsMean =  np.mean(data2)
  predMean = np.mean(data1)
  nmse = measure.nmse_1(data1, data2, cutoff=0.0)
  nmb  = measure.nmb(data1,data2)
  fac2 = measure.fac2(data1, data2)
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
    '''
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
        #plt.scatter(diff2,diff1,color='red')
        #plt.scatter(diff2,diff3,color='green')
        #plt.show()
      #plt.hold(False)
      #plt.show() 
    '''   
  #print 'getStats:'
  #print 'obs =',data2
  #print 'pre =',data1
  print 'Case,arc,stats: ',case,arc,obsMean, predMean, nmse, nmb, correlation, fac2
  if statFile is not None:
    #statFile.write("%s,%s,%8.3f, %8.3f, %8.3f, %8.3f\n"%(case, arc, upa, nmse, mfbe,fac2))
    statFile.write("%s, %s, %8.2f, %8.2f, %8.2f, %8.2f, %8.2f, %8.3f\n"%(case, arc, obsMean, predMean, nmse, nmb, correlation, fac2))    

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
  clr  = ['green','blue','red']
  
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
    if isColor:
      lh, = plt.plot(wVals,pdf,color=clr[i],marker=mark[i])
    else:            
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
  # plt.text(-1.5,-0.1,figCaption1,fontsize=10)#transform=ax.transAxes,
  plt.legend(lH,lT)
  plt.hold(False)
  #plt.show()
  if isColor:
    plt.savefig('Fig1_Color_w-pdf.png') #,dpi=300)
  else:
    plt.savefig('Fig1_w-pdf.png')#,dpi=300)
  #plt.savefig('w-pdf.eps',dpi=300)
  print "Done plotting w-pdf"
   
pltWPDF()

statFile = open("COP_stat.csv","w")
statFile.write("Case, Arc, ObsMean, PredMean, NMSE, NMB, Correlation, Fac2\n")

fileName = os.path.join(runDir,'cop_new.all')
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
if isColor:
  clr = ['red','blue','green']
else:
  clr = ['0.5','0.5','0.5']
#cMx = [[.5,8.],[0.,4.],[0.,3.]]
mSkw = ['o','*','s']
mStd = ['^','D','d']

fig = plt.figure()
plt.clf()
plt.hold(True)

phdl = []
plbl = []

for arc in range(3):
  
  stdCo = arcStdOP[arc,:,0]
  stdCp = arcStdOP[arc,:,1]
  stdCp = np.sort(stdCp)
  stdCp = ma.masked_where(stdCo<-98.0,stdCp)*1e-3
  stdCo = np.sort(stdCo)
  stdCo = ma.masked_where(stdCo<-98.0,stdCo)*1e-3
  
  skewCo = arcSkewOP[arc,:,0]
  skewCp = arcSkewOP[arc,:,1]
  skewCp = np.sort(skewCp)
  skewCp = ma.masked_where(skewCo<-98.0,skewCp)*1e-3
  skewCo = np.sort(skewCo)
  skewCo = ma.masked_where(skewCo<-98.0,skewCo)*1e-3
  
  print 'Arc = ',arc,skewCo[0],skewCp[0],stdCo[0],stdCp[0]
  #print 'std'
  #for i in range(len(stdCo)):
    #print i,stdCo[i],stdCp[i]
  #hstd  = plt.scatter(stdCo[:],stdCp[:],edgecolor='k',color=clr[arc],marker=mStd[arc],s=30)
    
  print 'skew sorted'
  for i in range(len(skewCp)):
    print i,skewCo[i],skewCp[i]
  #hskew = plt.scatter(skewCo[:],skewCp[:],edgecolor='k',color=clr[arc],marker=mSkw[arc],s=30)
  
  cSkewOP = ma.filled(cSkewOP,-99)
  for Cp in skewCp:
    try:
      smpNo = np.where(Cp == cSkewOP[:,1])[0][0]
    except IndexError:
      print 'Missing Cp = ',Cp
      continue
    print 'cSkewOP = ',arc,Cp,smpNo,cSkewOP[smpNo,0],cSkewOP[smpNo,1]
    hskew = plt.scatter(cSkewOP[smpNo,0],cSkewOP[smpNo,1],edgecolor='k',color=clr[arc],marker=mSkw[arc],s=30)
    hstd  = plt.scatter(cSkewOP[smpNo,0],cStdOP[smpNo,1],edgecolor='k',color=clr[arc],marker=mStd[arc],s=30)

  phdl.append(hskew)  
  plbl.append('Skewed   (Arc%d)'%(arc+1))
  
  '''
  cStdOP = ma.filled(cStdOP,-99)
  for Cp in stdCp:
    smpNo = np.where(Cp == cStdOP[:,1])[0][0]
    print 'cStdCp = ',arc,Cp,smpNo,cStdOP[smpNo,0],cStdOP[smpNo,1]
    #hstd  = plt.scatter(cStdOP[smpNo,0],cStdOP[smpNo,1],edgecolor='k',color=clr[arc],marker=mStd[arc],s=30)
  '''
  phdl.append(hstd)
  plbl.append('Standard (Arc%d)'%(arc+1))

  '''
  hskew = plt.scatter(cSkewOP[:,0],cSkewOP[:,1],color='black',marker='o',s=30)
  hstd  = plt.scatter(cStdOP[:,0],cStdOP[:,1],color='black',marker='^',s=30)

  hskew = plt.scatter(skewCo,skewCp,color='k',marker='o',s=30)
  hstd  = plt.scatter(stdCo,stdCp,color='k',marker='^',s=30)  
  '''
vmin = 0. #cMx[arc][0]
vmax = 8. #cMx[arc][1]
  
plt.xlim([vmin,vmax])
plt.ylim([vmin,vmax])
plt.plot([vmin,vmax],[vmin,vmax],'k-')
plt.xlabel(r'Observed ($\mu g/m^3$)', fontsize=10)
plt.ylabel(r'Predicted ($\mu g/m^3$)', fontsize = 10)
plt.legend(phdl,plbl,bbox_to_anchor=(0.25,0.97))
  
plt.hold(False)
#plt.show()
if isColor:
  pltName = 'Fig3_Color_cop_ord_arc.png'
else:
  pltName = 'Fig3_cop_ord_arc.png'  
plt.savefig(pltName) #,dpi=300)

# Plot based on stability classes

zMin = min(zoL)
zMax = max(zoL)

fig = plt.figure()
plt.clf()
plt.hold(True)

phdl = []
plbl = []

zl10 = []
zl5  = []
z11  = []

lgdList = []

for rNo in range(9):

  stdCo = arcStdOP[:,3*rNo:3*(rNo+1),0].flatten()
  stdCp = arcStdOP[:,3*rNo:3*(rNo+1),1].flatten()
  stdCp = ma.masked_where(stdCo<-98.0,stdCp)
  stdCp = np.sort(stdCp)*1e-3
  stdCo = ma.masked_where(stdCo<-98.0,stdCo)
  stdCo = np.sort(stdCo)*1e-3
  
  skewCo = arcSkewOP[:,3*rNo:3*(rNo+1),0].flatten()
  skewCp = arcSkewOP[:,3*rNo:3*(rNo+1),1].flatten()
  skewCp = ma.masked_where(skewCo<-98.0,skewCp)
  skewCp = np.sort(skewCp)*1e-3
  skewCo = ma.masked_where(skewCo<-98.0,skewCo)
  skewCo = np.sort(skewCo)*1e-3

  stdCo  = ma.filled(stdCo,-99)
  stdCp  = ma.filled(stdCp,-99)
  skewCo = ma.filled(skewCo,-99)
  skewCp = ma.filled(skewCp,-99)

  
  for c in zip(stdCo,stdCp,skewCo,skewCp):
    if zoL[rNo] > 10.:  #  [43.0,5.0,10.4,2.3,1.4,2.3,13.6,11.3,5.5]
      zl10.append(c)     
    elif zoL[rNo] > 4.:  #  [43.0,5.0,10.4,2.3,1.4,2.3,13.6,11.3,5.5]
      zl5.append(c)     
    else:  #  [43.0,5.0,10.4,2.3,1.4,2.3,13.6,11.3,5.5]
      z11.append(c)     

  print zl10
  print zl5
  print z11
  
  print 'runNo = ',rNo
  clr  = str((zoL[rNo]-zMin)/(zMax-zMin))
    
  print 'Run No. = ',rNo,skewCo[0],skewCp[0],stdCo[0],stdCp[0],zoL[rNo], pgt[rNo]
  #print 'std'
  #for i in range(len(stdCo)):
    #print i,stdCo[i],stdCp[i]
  #hstd  = plt.scatter(stdCo[:],stdCp[:],edgecolor='k',color=clr[arc],marker=mStd[arc],s=30)
    
  #print 'skew sorted'
  #for i in range(len(skewCp)):
  #  print i,skewCo[i],skewCp[i]
  #hskew = plt.scatter(skewCo[:],skewCp[:],edgecolor='k',color=clr[arc],marker=mSkw[arc],s=30)
  
  cSkewOP = ma.filled(cSkewOP,-99)
  for Cp in skewCp:
    try:
      smpNo = np.where(Cp == cSkewOP[:,1])[0][0]
    except IndexError:
      print 'Missing Cp = ',Cp
      continue
    print 'cSkewOP = ',rNo,Cp,smpNo,cSkewOP[smpNo,0],cSkewOP[smpNo,1],pgt[rNo]
    hskew = plt.scatter(cSkewOP[smpNo,0],cSkewOP[smpNo,1],edgecolor='k',color=pgt[rNo],marker='o',s=30)
    hstd  = plt.scatter(cSkewOP[smpNo,0],cStdOP[smpNo,1],edgecolor='k',color=pgt[rNo],marker='^',s=30)

  if pgt[rNo] not in lgdList:
    phdl.append(hskew)  
    if zoL[rNo] > 10.:  #  [43.0,5.0,10.4,2.3,1.4,2.3,13.6,11.3,5.5]
      plbl.append(r'Skewed   ($-z_i/L \geq 10$)')
    elif zoL[rNo] > 4.:  #  [43.0,5.0,10.4,2.3,1.4,2.3,13.6,11.3,5.5]
      plbl.append(r'Skewed   ($10 > -z_i/L \geq 4$)')
    else:  #  [43.0,5.0,10.4,2.3,1.4,2.3,13.6,11.3,5.5]
      plbl.append(r'Skewed   ($-z_i/L < 4$)')

    phdl.append(hstd)  
    if zoL[rNo] > 10.:  #  [43.0,5.0,10.4,2.3,1.4,2.3,13.6,11.3,5.5]
      plbl.append(r'Standard ($-z_i/L \geq 10$)')
    elif zoL[rNo] > 4.:  #  [43.0,5.0,10.4,2.3,1.4,2.3,13.6,11.3,5.5]
      plbl.append(r'Standard ($10 > -z_i/L \geq 4$)')
    else:  #  [43.0,5.0,10.4,2.3,1.4,2.3,13.6,11.3,5.5]
      plbl.append(r'Standard ($-z_i/L < 4$)')
    
    lgdList.append(pgt[rNo])

vmin = 0. #cMx[arc][0]
vmax = 8. #cMx[arc][1]
  
plt.xlim([vmin,vmax])
plt.ylim([vmin,vmax])
plt.plot([vmin,vmax],[vmin,vmax],'k-')
plt.xlabel(r'Observed ($\mu g/m^3$)', fontsize=10)
plt.ylabel(r'Predicted ($\mu g/m^3$)', fontsize = 10)
plt.legend(phdl,plbl,bbox_to_anchor=(0.32,0.98))
  
plt.hold(False)
#plt.show()
plt.savefig('cop_ord_pgt.png')

zl10 = np.array(zl10)
zl10 = ma.masked_where(zl10<-98.0,zl10)
zl5 = np.array(zl5)
zl5 = ma.masked_where(zl5<-98.0,zl5)
z11 = np.array(z11)
z11 = ma.masked_where(z11<-98.0,z11)

getStats(zl10[:,1], zl10[:,0], statFile, 'Std' ,'zl10')
getStats(zl10[:,3], zl10[:,2], statFile, 'Skew' ,'zl10')
getStats(zl5[:,1], zl5[:,0], statFile, 'Std' ,'zl5')
getStats(zl5[:,3], zl5[:,2], statFile, 'Skew' ,'zl5')
getStats(z11[:,1], z11[:,0], statFile, 'Std' ,'z11')
getStats(z11[:,3], z11[:,2], statFile, 'Skew' ,'z11')


# Unordered plot
fig = plt.figure()
plt.clf()
plt.hold(True)

plt.scatter(zl10[:,2],zl10[:,3],edgecolor='k',color='0.',marker='o',s=30)
plt.scatter(zl10[:,0], zl10[:,1],edgecolor='k',color='0.',marker='^',s=30)

plt.scatter(zl5[:,2],zl5[:,3],edgecolor='k',color='0.5',marker='o',s=30)
plt.scatter(zl5[:,0], zl5[:,1],edgecolor='k',color='0.5',marker='^',s=30)

plt.scatter(z11[:,2],z11[:,3],edgecolor='k',color='1.0',marker='o',s=30)
plt.scatter(z11[:,0], z11[:,1],edgecolor='k',color='1.0',marker='^',s=30)

vmin = 0. #cMx[arc][0]
vmax = 8. #cMx[arc][1]
  
plt.xlim([vmin,vmax])
plt.ylim([vmin,vmax])
plt.plot([vmin,vmax],[vmin,vmax],'k-')
plt.xlabel(r'Observed ($\mu g/m^3$)', fontsize=10)
plt.ylabel(r'Predicted ($\mu g/m^3$)', fontsize = 10)
plt.legend(phdl,plbl,bbox_to_anchor=(0.32,0.98))
  
plt.hold(False)
plt.show()


print 'Done plotting in ',os.getcwd()


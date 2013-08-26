import os
os.chdir("D:\\Documents\\SCICHEM\\SCICHEM-3.0\\AWMA-AQ2013\\130811")
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

font0 = FontProperties()
font_bold = font0.copy()
font_bold.set_weight('bold')

for fNo in ['1','2a','2b']: # ['1','2a','2b']:
  if fNo == '1':
    arry = np.loadtxt('SCIPUFF-CalcsVsObsLowWind_IF.prn',skiprows=2)
  elif fNo[0] == '2':
    arry = np.loadtxt('SCIPUFF-CalcsVsObsLowWind_OR.prn',skiprows=2)
  arry = ma.masked_where(arry<0,arry)
  SCIdata = arry[:,0]
  ObsData = arry[:,3]
  AerbData = arry[:,1]
  AeraData = arry[:,2]
  plt.rc('legend',**{'fontsize':10})
  plt.rc('legend',**{'markerscale':0.7})
  plt.rc('xtick',**{'labelsize':10})
  plt.rc('ytick',**{'labelsize':10})
  plt.rc('axes',**{'labelsize':12})
  vmin = 0.
  fig = plt.figure()
  plt.clf()
  fig.subplots_adjust(bottom=0.25)
  #fig.subplots_adjust(left=0.12)
  #fig.subplots_adjust(right=0.87)
  #fig.subplots_adjust(top=0.95)
  ax = fig.add_subplot(111)  
  plt.hold(True)
  if fNo == '1':
    vmax = 180.  #max(ObsData.max(),SCIdata.max(),Aer1Data.max(),Aer2Data.max())
    hsci  = plt.scatter(ObsData,SCIdata,marker='s',color='black',s=50)
    haerb = plt.scatter(ObsData,AerbData,marker='o',color='black',s=50)
    haera = plt.scatter(ObsData,AeraData,marker='^',color='black',s=50)
    plt.xlim([vmin,vmax])
    ax.set_aspect('1')
    figCapNo    = r'Figure 1.'
    figCaption1 = r'Scatter plot for Idaho Falls observed and predicted hourly-averaged'
    figCaption2 = r"arc-maximum concentrations for SCICHEM and for two AERMOD versions."
    figCaption3 = r"The AERMOD (Base) model is the EPA's current operational version 12345 "
    figCaption4 = r'and the AERMOD (Beta 4) model is option 4 with adjusted $u_*$ and $\sigma_v$= 0.3 m/sec.'
    plt.text(-0.4,-0.17,figCapNo,fontsize=13,transform=ax.transAxes,fontproperties=font_bold)
    plt.text(-0.15,-0.17,figCaption1,fontsize=13,transform=ax.transAxes)
    plt.text(-0.4,-0.22 ,figCaption2,fontsize=13,transform=ax.transAxes)
    plt.text(-0.4,-0.27,figCaption3,fontsize=13,transform=ax.transAxes)
    plt.text(-0.4,-0.32,figCaption4,fontsize=13,transform=ax.transAxes)
    plt.legend([hsci,haerb,haera],[r'SCICHEM',r'AERMOD (Base)',r'AERMOD (Beta 4)'],bbox_to_anchor=(0.99,0.2))
  elif fNo == '2a':
    vmin = min(ObsData.min(),AerbData.min())
    vmax = max(ObsData.max(),AerbData.max()) #1000.
    Obs = np.array(ObsData[:-1])
    Aer = np.array(AerbData[:-1])
    print Obs.max()
    print Aer.max()
    vmin = 0.
    vmax = 1300 
    obsMax = 130
    haerb = plt.scatter(Obs,Aer,marker='o',color='black',s=50)
    plt.xlim([vmin,obsMax])
    #ax.set_aspect('equa')
    aspect = 10
    ax.set_aspect(0.1)
    figCapNo    = r'Figure 2a.'
    figCaption1 = r'Scatter plot for Oak Ridge observed and predicted hourly-'
    figCaption2 = r"averaged arc-maximum concentrations for the AERMOD (Base)"
    figCaption3 = r"operational model version 12345."
    plt.text(-0.35,-0.17,figCapNo,fontsize=13,transform=ax.transAxes,fontproperties=font_bold)
    plt.text(-0.07,-0.17,figCaption1,fontsize=13,transform=ax.transAxes)
    plt.text(-0.35,-0.22 ,figCaption2,fontsize=13,transform=ax.transAxes)
    plt.text(-0.35,-0.27,figCaption3,fontsize=13,transform=ax.transAxes)
    ''' 
    # Aspect ratio 10
    
    obsMax = 200
    haerb = plt.scatter(Obs,Aer,marker='o',color='black',s=50)
    plt.xlim([vmin,obsMax])
    ax.set_aspect('equal')
    ax.set_xticks([0.,obsMax])
    ax.set_xticklabels([0.,obsMax])
    figCapNo    = r'Figure 2a.'
    figCaption1 = r'Scatter plot for OakRidge observed and predicted hourly-averaged'
    figCaption2 = r"arc-maximum concentrations for the AERMOD Base model (EPA's current "
    figCaption3 = r'operational model)'
    plt.figtext(0.1, 0.13,figCapNo,fontsize=13,fontproperties=font_bold)
    plt.figtext(0.24, 0.13,figCaption1,fontsize=13)
    plt.figtext(0.1, 0.08,figCaption2,fontsize=13)
    plt.figtext(0.1, 0.03,figCaption3,fontsize=13)
    #plt.legend([haerb,],[r'AERMOD(Base)',],loc='center left', bbox_to_anchor=(1, 0.1))
    '''
  elif fNo == '2b':
    vmax = 120. 
    hsci  = plt.scatter(ObsData,SCIdata,marker='s',color='black',s=50)
    haera = plt.scatter(ObsData,AeraData,marker='^',color='black',s=50)
    plt.xlim([vmin,vmax])
    ax.set_aspect('1')
    figCapNo    = r'Figure 2b.'
    figCaption1 = r'Scatter plot for Oak Ridge observed and predicted hourly-averaged'
    figCaption2 = r"arc-maximum concentrations for SCICHEM and for AERMOD (Beta 4),"
    figCaption3 = r'which is option 4 with adjusted $u_*$ and $\sigma_v$= 0.3 m/sec.'
    plt.text(-0.4,-0.17,figCapNo,fontsize=13,transform=ax.transAxes,fontproperties=font_bold)
    plt.text(-0.12,-0.17,figCaption1,fontsize=13,transform=ax.transAxes)
    plt.text(-0.4,-0.22 ,figCaption2,fontsize=13,transform=ax.transAxes)
    plt.text(-0.4,-0.27,figCaption3,fontsize=13,transform=ax.transAxes)    
    plt.legend([hsci,haera],[r'SCICHEM',r'AERMOD (Beta 4)'],bbox_to_anchor=(0.99,0.17))    
  plt.ylim([vmin,vmax])
  plt.plot([vmin,vmax],[vmin,vmax],'k-')
  #plt.plot([vmin,vmax],[vmin*0.5,vmax*0.5],'k-')
  #plt.plot([vmin,vmax],[vmin*2,vmax*2],'k-')
  plt.xlabel(r'Observed Concentrations($\mu g/m^3$)')
  plt.ylabel(r'Predicted Concentrations($\mu g/m^3$)')
  plt.hold(False)
  plt.savefig('Figure%s.eps'%fNo,dpi=300)
  #plt.savefig('Figure%s.png'%fNo,dpi=300)
  plt.show()
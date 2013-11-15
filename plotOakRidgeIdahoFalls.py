import os
os.chdir("D:\\Documents\\SCICHEM\\SCICHEM-3.0\\AWMA-AQ2013\\130811")
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

font0 = FontProperties()
font_bold = font0.copy()
font_bold.set_weight('bold')

for fNo in ['2']:
  if fNo == '1':
    arry = np.loadtxt('SCIPUFF-CalcsVsObsLowWind_IF.prn',skiprows=2)
  elif fNo == '2':
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
  
  #fig.subplots_adjust(left=0.12)
  #fig.subplots_adjust(right=0.87)
  #fig.subplots_adjust(top=0.95)
  if fNo == '1':
    ax = fig.add_subplot(111)  
    fig.subplots_adjust(bottom=0.25)
    plt.hold(True)
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
    plt.ylim([vmin,vmax])
    plt.plot([vmin,vmax],[vmin,vmax],'k-')
    #plt.plot([vmin,vmax],[vmin*0.5,vmax*0.5],'k-')
    #plt.plot([vmin,vmax],[vmin*2,vmax*2],'k-')
    plt.xlabel(r'Observed Concentrations($\mu g/m^3$)')
    plt.ylabel(r'Predicted Concentrations($\mu g/m^3$)')
  
  elif fNo == '2':
    
   
    # Subplot 2a
    ax1 = fig.add_subplot(121)  
    fig.subplots_adjust(bottom=0.25,hspace=-2.5)
    plt.hold(True)
    plt.text(0.48,1.04,'(a)',fontsize=13,transform=ax1.transAxes,fontproperties=font_bold)
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
    #ax.set_aspect('equal')
    aspect = 10
    ax1.set_aspect(0.1)
    plt.ylim([vmin,vmax])
    plt.plot([vmin,vmax],[vmin,vmax],'k-')
    #ax.set_xticklabels([])
    plt.xlabel(r'Observed Concentrations($\mu g/m^3$)')
    #plt.ylabel(r'Predicted Concentrations($\mu g/m^3$)')
    ax1.set_ylabel(r'Predicted Concentrations($\mu g/m^3$)')
    ax1.yaxis.set_label_coords(-0.15, 0.5)
    ax1.legend([haerb,],['AERMOD (Base)',],loc=(0.4,0.88)) 
    # Subplot 2b
    ax2 = fig.add_subplot(122)  
    plt.text(0.5,1.02,'(b)',fontsize=13,transform=ax2.transAxes,fontproperties=font_bold)
    vmax = 120. 
    hsci  = plt.scatter(ObsData,SCIdata,marker='s',color='black',s=50)
    haera = plt.scatter(ObsData,AeraData,marker='^',color='black',s=50)
    plt.xlim([vmin,vmax])
    ax2.set_aspect('1')
    plt.legend([hsci,haera],[r'SCICHEM',r'AERMOD (Beta 4)'],bbox_to_anchor=(0.99,0.2))    
    plt.ylim([vmin,vmax])
    plt.plot([vmin,vmax],[vmin,vmax],'k-')
    plt.xlabel(r'Observed Concentrations($\mu g/m^3$)')
    #plt.ylabel(r'Predicted Concentrations($\mu g/m^3$)')
    #ax2.set_ylabel(r'Predicted Concentrations($\mu g/m^3$)')
    #ax2.yaxis.set_label_coords(-0.1, 0.5)
  
    figCapNo    = r'Figure 2.'
    figCaption1 = r'Scatter plot for Oak Ridge observed and predicted hourly-averaged'
    figCaption2 = r"arc-maximum concentrations for (a) AERMOD (Base) operational model version"
    figCaption3 = r"12345 and (b) SCICHEM and AERMOD (Beta 4), which is option 4 with adjusted $u_*$"
    figCaption4 = r'and $\sigma_v$= 0.3 m/sec.'
    
    plt.text(-1.4,-0.27,figCapNo,fontsize=13,transform=ax2.transAxes,fontproperties=font_bold)
    plt.text(-1.05,-0.27,figCaption1,fontsize=13,transform=ax2.transAxes)
    plt.text(-1.4,-0.34 ,figCaption2,fontsize=13,transform=ax2.transAxes)
    plt.text(-1.4,-0.41,figCaption3,fontsize=13,transform=ax2.transAxes)    
    plt.text(-1.4,-0.48,figCaption4,fontsize=13,transform=ax2.transAxes)    

  plt.hold(False)
  plt.savefig('Figure%s.eps'%fNo,dpi=300)
  #plt.savefig('Figure%s.png'%fNo,dpi=300)
  plt.show()
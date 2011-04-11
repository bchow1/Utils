#!/bin/env /bin/python
import os
import sys
import subprocess
from numpy import *
import matplotlib

def setParams(clrlev,clrmin,clrmax,logScale=True,fext='.pdf'):

  if fext == '.pdf':
    matplotlib.use('pdf')

  import matplotlib.pyplot as plt
  import matplotlib.cm as cm
  from matplotlib import colors

  params1 = {'axes.labelsize': 10, 'text.fontsize': 10, 'xtick.labelsize': 10,
              'ytick.labelsize': 10, 'legend.pad': 0.1,  # empty space around the legend box
              'legend.fontsize': 8, 'lines.markersize': 6, 'lines.width': 2.0,
              'font.size': 10, 'text.usetex': False}

  plt.rcParams.update(params1)

  if fext == '.eps':

    print 'Resetting parameters. Backend is set to postscript'

    # Set size
    fig_width_pt = 246.0                    # Get this from LaTeX using \showthe\columnwidth
    inches_per_pt = 1.0/72.27               # Convert pt to inches
    golden_mean = (sqrt(5)-1.0)/2.0         # Aesthetic ratio
    fig_width = fig_width_pt*inches_per_pt  # width in inches
    fig_height =fig_width*golden_mean       # height in inches
    fig_size = [fig_width,fig_height]

    params1 = {'backend': 'ps', 'figure.figsize': fig_size}
    #params = {'backend': 'ps', 'axes.labelsize': 10, 'text.fontsize': 10, 'legend.fontsize': 10,
    #          'xtick.labelsize': 8, 'ytick.labelsize': 8, 'text.usetex': True, 'figure.figsize': fig_size}

    plt.rcParams.update(params1)

  ccolor  = [ 'red', 'blue', 'green', 'cyan', 'magenta', 'lime', 'olive', 'maroon', 'teal', 'purple' ]
  #ccolor = [ 'aqua', 'navy', 'fuchsia', 'yellow' ]

  cmarker = [ 'o', 'd', '^', 'v', '>', '<', 's', '+', 'x', '*', 'p', 'h' ]
  #cmarker = [ '1', '2', '3', '4' ]

  if logScale:
    levels = logspace(clrmin,clrmax,num=clrlev,base=10.0)
    clrmap = cm.get_cmap('jet',clrlev-1)
    lnorm  = colors.LogNorm(levels,clip=False)
  else:
    levels = linspace(clrmin,clrmax,num=clrlev)
    clrmap = cm.get_cmap('jet',clrlev-1)
    lnorm  = colors.Normalize(levels,clip=False)
      
  return (plt, ccolor, cmarker, levels, clrmap, lnorm)

class Plots(object):
    
  def __init__(self,clrLev=8,clrMin=-6,clrMax=1,logScale=True,fext='.pdf'):
    self.figno       = 0
    self.xlabel      = ""
    self.ylabel      = ""
    self.xlim        = None
    self.ylim        = None
    self.title       = None
    self.flist       = []
    self.fext        = fext
    self.cscale      = None
    self.clrLev      = clrLev
    self.clrMin      = clrMin
    self.clrMax      = clrMax
    self.logScale    = logScale
    # Setup plot parameters
    (self.plt, self.ccolor, self.cmarker, self.levels, self.clrMap, self.lnorm ) \
                     =  setParams(self.clrLev,self.clrMin,self.clrMax,self.logScale,self.fext)
    self.vmin        = self.levels[0]
    self.vmax        = self.levels[self.clrLev-1]
    print 'In PlotSampler.Plots, minmax color range = ',self.vmin,',',self.vmax
    print 'In PlotSampler.Plots, levels = ',self.levels
    print 'In PlotSampler.Plots, lnorm = ',self.lnorm

  def back2d(self,mySamplerSet,fig,figName):
    self.plt.clf()
    self.plt.hold(True)
    self.plt.xlabel(self.xlabel)
    self.plt.ylabel(self.ylabel)
    if self.title:
      title = self.title
    elif self.cscale:
      title = '%s scaled by %8.3e'% (figName,self.cscale)
    else:
      title = '%s'% figName
    fig.suptitle(title, fontsize=11, fontweight='bold')
    # Plot additional points if provided
    for mySource in mySamplerSet.pntarry:     
      #print mySource.x, mySource.y,'%s' % mySource.label
      # Skip if outside limits
      if self.xlim:
        if mySource.x < self.xlim[0] or mySource.x > self.xlim[1]:
          continue
      if self.ylim:
        if mySource.y < self.ylim[0] or mySource.y > self.ylim[1]:
          continue             
      x = array([mySource.x])
      y = array([mySource.y])
      self.plt.plot(x,y,mySource.pt)
      if mySource.xytext:
        self.plt.annotate('%s' % mySource.label,xy=(mySource.x,mySource.y),
                     xytext=mySource.xytext,arrowprops=mySource.aprop)
      else:
        self.plt.text(mySource.x,mySource.y,'%s' % mySource.label,fontsize=mySource.fs)

    for mySampler in mySamplerSet.smparry:
      x = array([mySampler.x])
      y = array([mySampler.y])
      self.plt.text(mySampler.x,mySampler.y+mySamplerSet.dy/2,'%d' % mySampler.id,fontsize=9)

  def conc3d(self,mySamplerSet,saveFig=True,contour=False):

    # Concentration 3d plots for time t
    nt = len(mySamplerSet.smparry[0].Data['time'])
    for it in range(nt):
      tsec = mySamplerSet.smparry[0].Data['time'][it]
      if tsec < mySamplerSet.tmin or tsec > mySamplerSet.tmax:
        continue 
      self.figno = self.figno + 1
      fig        = self.plt.figure(self.figno)
      figName    = '%s concentration at %8.3f sec '%(mySamplerSet.name,tsec)

      # Plot 2d background
      self.back2d(mySamplerSet,fig,figName)

      # Get conc array for all samplers for time break it
      timarry = mySamplerSet.sam2tim(it=it,vnames=['conc'],vscale=self.cscale)

      if contour:
        # Get concetration on a grid and plot contours
        (X,Y,Concs) = mySamplerSet.sam2grd(varry=timarry,vnames=['conc'],
                                     xlim=self.xlim,ylim=self.ylim,nx=50,ny=50)
        C = Concs[0]
        if contour == "full":
          cset1 = self.plt.contourf(X,Y,C,self.clrLev,norm=self.lnorm,cmap=self.clrMap) 
        else:
          cset2 = self.plt.contour(X,Y,C,self.clrLev,norm=self.lnorm,cmap=self.clrMap)  

      # Plot sampler points with color based on conc value
      self.plt.scatter(timarry['x'],timarry['y'],c=timarry['conc'],edgecolors='none',marker='o',
                      vmin=self.vmin,vmax=self.vmax,norm=self.lnorm,cmap=self.clrMap)

      # Add conc value labels or black point
      for tarry in timarry:
        if tarry['conc'] > 0. :
          self.plt.text(tarry['x'],tarry['y']-mySamplerSet.dy/2,'%6.4f' % tarry['conc'],fontsize=9)
        else:
          x = [tarry['x']]
          y = [tarry['y']]
          self.plt.plot(x,y,'ko')
      self.plt.colorbar(fraction=0.08)
      fname = mySamplerSet.name + "_time%03d"%it + self.fext
      print 'Creating ',fname
      self.flist.append(fname)
      if self.xlim:
        self.plt.xlim(self.xlim)
      if self.ylim:
        self.plt.ylim(self.ylim)
      self.plt.hold(False)
      self.plt.savefig(fname)
    return
     
  def maxConc(self,mySamplerSet,saveFig=True):
    # Maximum concentration plots
    self.figno = self.figno + 1
    fig = self.plt.figure(self.figno)
    figName = '%s maximum concentration '% mySamplerSet.name
    self.back2d(mySamplerSet,fig,figName)
    for mySampler in mySamplerSet.smparry:
      x = array([mySampler.x])
      y = array([mySampler.y])         
      if mySampler.maxCt > mySamplerSet.czero:
        if self.cscale:
          Cscaled = array([mySampler.maxCt/self.cscale])
        else:
          Cscaled = array([mySampler.maxCt/mySamplerSet.cmax])
        self.plt.scatter(x,y,c=Cscaled,edgecolors='none',marker='o',
                      vmin=self.vmin,vmax=self.vmax,norm=self.lnorm,cmap=self.clrMap)
        self.plt.text(mySampler.x,mySampler.y-mySamplerSet.dy/2,'%6.4f' % Cscaled,fontsize=9)
      elif mySampler.maxCt < 0:
        self.plt.plot(x,y,'gx')        
      else:
        self.plt.plot(x,y,'ko')
      #print x, y, mySampler.id, mySampler.maxCt
    self.plt.colorbar(fraction=0.08)
    fname = mySamplerSet.name + "_Max" + self.fext
    print 'Creating ',fname
    self.flist.append(fname)
    if self.xlim:
      self.plt.xlim(self.xlim)
    if self.ylim:
      self.plt.ylim(self.ylim)
    if saveFig:
      self.plt.hold(False)
      self.plt.savefig(fname)
    return(self.plt,fname)

  def timeSeries(self,mySamplerSets,nsub=2,nsmp=2,msize=4):
    ''' nsub = number of subplots in the figure
        nsmp = number of samplers in each subplot'''
    if msize:
      params1 = {'lines.markersize':msize}
      self.plt.rcParams.update(params1)
    
    FirstSamplerSet = mySamplerSets[0]
    nSet            = len(mySamplerSets)
    print 'tmin, tmax = ',FirstSamplerSet.tmin, FirstSamplerSet.tmax
    if FirstSamplerSet.cmax < 0.:
      print 'Error:',FirstSamplerSet.name,' cmax not set' 
      sys.exit()
    if FirstSamplerSet.ccut < 0.:
      if FirstSamplerSet.czero > 0.:
        print 'Warning: ',FirstSamplerSet.name,' ccut not set'
        print '         Using czero*10 = ',FirstSamplerSet.czero*10.,' as ccut'
        FirstSamplerSet.ccut = FirstSamplerSet.czero*10.
      else:
        print 'Error:',FirstSamplerSet.name,' ccut and czero not set' 
        sys.exit()
    print 'clow, chigh = ',FirstSamplerSet.ccut*0.1, FirstSamplerSet.cmax*10
    Nlim = int(log10(FirstSamplerSet.cmax*10./(FirstSamplerSet.ccut*0.1)) + 0.5)
    Clim = zeros((2,Nlim+1), float)
    if FirstSamplerSet.tmax > 3600.:
      tScale = 3600.
      tUnit  = 'hr'
    elif FirstSamplerSet.tmax > 60.:
      tScale = 60.
      tUnit  = 'min'
    else:
      tScale = 1.
      tUnit  = 'sec'
    Clim[0,0] = FirstSamplerSet.tmin/tScale
    Clim[1,0] = FirstSamplerSet.tmax/tScale
    for i in range(1,Nlim+1):
      Clim[:,i] = 0.1*FirstSamplerSet.ccut*10.**i 
    
    for mySampler in FirstSamplerSet.smparry:
      if mySampler.id%(nsmp*nsub) == 1:
        self.figno = self.figno + 1
        fig = self.plt.figure(self.figno)
        self.plt.clf()
        count = 0
        fig.text(0.02,0.5,'Conc(kg/m3)',rotation='vertical')
        for i in range(nSet):
          if i == 0:
            Stitle = mySamplerSets[i].name
          else:
            Stitle = Stitle + ' and ' + mySamplerSets[i].name
        Stitle = Stitle + (' concentrations\n (Start time %s, Avg. time = %d %s)'% 
                             (FirstSamplerSet.startTime, FirstSamplerSet.tavg/tScale, tUnit))
        if self.title:
          Stitle = self.title
        fig.suptitle(Stitle, fontsize=11, fontweight='bold')
      if mySampler.id%nsmp == 1:
        count = count + 1
        subno = nsub*100 + 10 + count
        ax = fig.add_subplot(subno)
        ax.hold(True)
        LgHdl = []
        LgLbl = []
        if subno == (nsub*100+10+nsub):
          if self.xlabel:
            ax.set_xlabel(self.xlabel)
          else:
            ax.set_xlabel("Time(%s)"%tUnit)
        else :
          ax.set_xticklabels([])
      addID = True
      tSeries = FirstSamplerSet.getTseries(mySamplerSets,id=mySampler.id,vnames=['conc'])
      print 'id = ',mySampler.id,
      print tSeries[0]['conc']
      print
      if addID:
        plabel = str(mySampler.id)        
        cmark  = self.cmarker[mySampler.id%nsmp]
        Lh = None
        for i in range(nSet):
          C = tSeries[i]['conc']
          C = ma.masked_where(C<=FirstSamplerSet.ccut*0.1, C)
          #print '** plot obs with cmark = ',cmark
          LhO = ax.plot(tSeries[i]['time']/tScale,C,marker=cmark,color=self.ccolor[i])
          #print '** plot obs with cmark = ',cmark
          #print i,tSeries[i]['time']/tScale,C
          if not Lh:
            Lh  = LhO
        LgHdl.append(Lh)
        LgLbl.append(plabel)
       
      if mySampler.id%nsmp == 0: 
        ax.plot(Clim[:,0],Clim[:,1],'m-')
        for i in range(2,Nlim+1):
          ax.plot(Clim[:,0],Clim[:,i],'k-')        
        if LgLbl:
          if len(LgLbl) > 0:
            ax.legend((LgHdl),(LgLbl),loc=(1.0,0.0))   # sampler numbers
        
        ax.set_xlim(FirstSamplerSet.tmin,FirstSamplerSet.tmax)
        ax.set_ylim(FirstSamplerSet.ccut*0.1,FirstSamplerSet.cmax*10)
        ax.set_yscale('log')
        ax.hold(False)
    
      if mySampler.id%(nsmp*nsub) == 0:
        LgdH = [[] for i in range(nSet)]
        LgdV = [[] for i in range(nSet)]
        for i in range(nSet):
          LgdH[i] = self.plt.Rectangle( (0,0), 1,1, facecolor=self.ccolor[i] )
          LgdV[i] = mySamplerSets[i].name
          
        if self.fext == '.pdf': 
          axl = self.plt.axes([0.55,0.03,0.3,0.01],frameon=False)   # Concentration type
        else:
          axl = self.plt.axes([0.70,0.05,0.3,0.01],frameon=False)    # Concentration type
        axl.xaxis.set_visible(False)
        axl.yaxis.set_visible(False)
        #print 'Adding legend type'
        l = axl.legend(LgdH,LgdV,ncol=nSet,borderaxespad=0.01)
        
      if mySampler.id%(nsmp*nsub) == 0:
        fname=str("smp_%03d" % self.figno) + self.fext
        self.plt.savefig(fname)
        if self.fext == '.pdf':
          self.flist.append(fname)
        
      if self.fext != '.pdf' and self.figno > 30:
        print 'Warning: Too many figure in non-pdf mode. Quiting'
        sys.exit()

def joinPDF(flist,fname):
  command = [["gs","-dBATCH","-dNOPAUSE","-q","-sDEVICE=pdfwrite","-sOutputFile=%s" % fname],\
             ["rm","-f"]]
  for cmd in command:
    cmd.extend(flist)
    (output, errmsg) = subprocess.Popen(cmd,stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE).communicate()
    if len(errmsg) > 0:
      print 'output = %s' % output
      print 'errmsg = %s' % errmsg
    else:
      if cmd == command[0]:
        print 'Combining output pdf files to create %s\n' % fname
  flist = []


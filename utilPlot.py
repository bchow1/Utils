#
'''
Utilities for initializing and setting plot parameters. 
Must use the utilPlot.plt command
'''
import os

def initParams(fext='.pdf'):
  '''
  Set backend and default label font, size etc.
  '''
  
  import matplotlib

  if fext == '.pdf':
    matplotlib.use('pdf')
 
  import matplotlib.pyplot as plt

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

  return(plt, ccolor, cmarker)
  
def setLevels(clrlev,clrmin,clrmax,logScale=True,logBase=None):
   
  import numpy as np
  import matplotlib.cm as cm
  from matplotlib import colors
 
  if logScale:
    if logBase is None:
      logBase = 10.
    levels = np.logspace(clrmin,clrmax,num=clrlev,base=logBase)
    clrmap = cm.get_cmap('jet',clrlev-1)
    lnorm  = colors.LogNorm(levels,clip=False)
  else:
    levels = np.linspace(clrmin,clrmax,num=clrlev)
    clrmap = cm.get_cmap('jet',clrlev-1)
    lnorm  = colors.Normalize(levels,clip=False)

  print levels
      
  return(levels, clrmap, lnorm)

def joinPDF(flist,fname):

  import subprocess
  import socket

  compName = socket.gethostname()
  env      = os.environ.copy()

  # Local modules
  if compName == 'sm-bnc' or compName == 'sage-d600':
    GS = "C:\\cygwin\\bin\\gs"
    RM = "C:\\cygwin\\bin\\rm"
  else:
    GS = 'gs'
    RM = 'rm'

  command = [[GS,"-dBATCH","-dNOPAUSE","-q","-sDEVICE=pdfwrite","-sOutputFile=%s" % fname],\
             [RM,"-f"]]
  for cmd in command:
    cmd.extend(flist)
    (output, errmsg) = subprocess.Popen(cmd,stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,env=env).communicate()
    #if len(errmsg) > 0:
    print 'output = %s' % output
    print 'errmsg = %s' % errmsg
    #else:
    #  if cmd == command[0]:
    #    print 'Combining output pdf files to create %s\n' % fname
  flist = []
  return flist

class Plot(object):
    
  def __init__(self,clrLev=8,clrMin=-6,clrMax=1,logScale=True,fext='.pdf',logBase=None):
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
    self.logBase     = logBase
    # Setup plot parameters
    (self.plt, self.ccolor, self.cmarker) =  initParams(self.fext)
    if clrLev > 0:
      setClrLev(self.clrLev,self.clrMin,self.clrMax,self.logScale,logBase=self.logBase)
 
  def setClrLev(self,clrLev=8,clrMin=-6,clrMax=1,logScale=True,logBase=None):
    self.clrLev      = clrLev
    self.clrMin      = clrMin
    self.clrMax      = clrMax
    self.logScale    = logScale
    self.logBase     = logBase
    (self.levels, self.clrMap, self.lnorm ) \
                     =  setLevels(self.clrLev,self.clrMin,self.clrMax,self.logScale,logBase=self.logBase)
    self.vmin        = self.levels[0]
    self.vmax        = self.levels[self.clrLev-1]
    print 'In utilPlot.Plot:'
    print '  color range = ',self.vmin,',',self.vmax
    print '  levels = ',self.levels
    print '  lnorm = ',self.lnorm,'\n'

if __name__ == '__main__':

  os.chdir('D:\\Aermod\\v12345\\runs\\kinsf6')
  fList = []
  for fName in os.listdir('.'):
    if fName.endswith('.pdf') or fName.endswith('.PDF'):
      fList.append(fName)
  joinPDF(fList,'test.pdf')


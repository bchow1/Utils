# copied from d:\NCEPplots. Does not work for rewriteAERMet 
import sys
from distutils.core import setup
import py2exe
import matplotlib
#matplotlib.use('agg') # overrule configuration
import pylab

sys.argv = ['','py2exe']
setup(console=['rewriteAERMet.py'],data_files=matplotlib.get_py2exe_datafiles())

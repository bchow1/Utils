
#!/bin/env python
import os
import sys
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import sqlite3

# Local modules
sys.path.append('C:\\cygwin\\home\\sid\\python')
import utilDb

# Code for SCIChem 2012 plots

def mainProg(obsDbName,preDbName1,preDbName2):


  # Observed data
  obsConn = sqlite3.connect(obsDbName)
  obsConn.row_factory = sqlite3.Row
  obsCur = obsConn.cursor()

  # Predicted data
  preConn1 = sqlite3.connect(preDbName1)
  preConn1.row_factory = sqlite3.Row
  preCur1 = preConn1.cursor()

  # Predicted data
  #preConn2 = sqlite3.connect(preDbName2)
  #preConn2.row_factory = sqlite3.Row
  #preCur2 = preConn2.cursor()
  
  plotConcAll(obsCur,preCur1)
  
  obsConn.close()
  preConn1.close()

  return

def plotCompConc(zSmp, varName, obsData, preData1, title):
  #import pdb; pdb.set_trace()
  fig = plt.figure()
  plt.clf()
  fig.hold(True)
  print obsData[:,1]
  plt.plot(obsData[:,1],'go')
  plt.plot(preData1[:])
  plt.ylabel(zSmp)
  plt.xlabel(varName)
  plt.title(title)
  fig.hold(False)
  plt.show()
        
def plotConcAll(obsCur, preCur1):
  
  varNames   = ["C004_","C002_", "C052_", "C001_"]
  varSpecies = ["O3", "NO", "SO2", "NO2"]
  
  time = 11.5
  
  for zSmp in [415]:  #[415, 582, 584]
    for i,varName in enumerate(varNames):

      # Observations
      obsQry = 'select plumeKM, ' + varSpecies[i] + ' from dataTable'
      obsArray = utilDb.db2Array(obsCur,obsQry)

      # Predictions #1 (2012) 
      preQry1 = "select value from smpTable  where colNo in \
                (select colNo from samTable  where varName = '%s' and zSmp = %f) and time = %3f"%(varName,zSmp, time)
      preArray1 = utilDb.db2Array(preCur1,preQry1)

      #
      plotCompConc(zSmp, varName, obsArray, preArray1, varSpecies[i])
    
# Main program
if __name__ == '__main__':
  obsDbName = 'tva_071599_16km_obs1.csv.db'
  preDbName1 = 'tva_071599.smp.db'
  preDbName2 = 'tva_071599.smp.db'
  print "Creating plots for ",obsDbName,preDbName1,preDbName2
  mainProg(obsDbName,preDbName1,preDbName2)

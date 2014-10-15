#!/bin/env python
import os
import sys
import re
import fileinput
import numpy as np
import matplotlib.pyplot as plt

class tstSuite:
  
  def __init__(self,name):
    print 'Create mySuite ',name
    self.name    = name
    self.inpDir  = []
    self.outDir  = []
    self.prjList = []
    self.pltList = []
  
  def addPrj(self,prjName):
    self.prjList.append(prjName)
    
  def addPlt(self,pltName):
    self.pltList.append(pltName)

os.chdir('D:\\TestHPAC\\Scripts')
suiteList = []
mySuite   = None
isCase    = False
for line in fileinput.input('runlist.sh'):
  if "case" in line:
    isCase = True
    prjDir = None
    continue
  if "esac" in line:
    isCase = False
    break
  if isCase:
    if line.rstrip().endswith('")'):
      if mySuite is not None:
        suiteList.append(mySuite)
      mySuite = tstSuite(line.strip().replace(')','').replace('"',''))
    if "DIR=" in line:
      line  = line.strip().replace('"','').replace(';','')
      dName = line.split('=')[1].replace('${RUN}',mySuite.name)
      if "INPDIR=" not in line and "OUTDIR=" not in line:
        prjDir = dName
        print prjDir
    if "PlotList" in line:
      pltNames = line.split('=')[1].replace('${PlotList[@]}','').replace(';','').replace('(','').replace(')','').split()
      for pltName in pltNames:
        mySuite.addPlt(pltName)
fileinput.close()

regDir = 'b225x64'
outDir = '2014.10.09'
os.chdir('D:\\TestHPAC\\Outputs')

htmlFile = open('RegressionReport.html','w')
docType = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
docType += '<head><meta content="text/html; charset=ISO-8859-1" http-equiv="content-type"><title>Regression Test Results</title>\n'
docType += '  <style type="text/css"></style>\n'
docType += '  <link href="reports.css" type="text/css" rel="stylesheet" /></head>\n'
docType += ' <body>\n'
htmlFile.write(docType)
      
for suite in suiteList:
  htmlFile.write('<h1>') 
  htmlFile.write(suite.name)
  htmlFile.write('</h1>\n') 
  #htmlFile.write(suite.pltList)
  print suite.pltList
  for pltName in suite.pltList:
      if '.' in pltName:
        writeAsTest()
        htmlFile = open('RegressionReport.html','w')
      else:        
        htmlFile.write('<p>Plot for version:%s<br>'%regDir)
        htmlFile.write('<img  alt="%s Plot" src="%s/plots/%s.png">' %(pltName,regDir,pltName)) 
        htmlFile.write('<p>Plot for version:%s<br>'%outDir)
        htmlFile.write('<img  alt="%s Plot" src="%s/plots/%s.png">' %(pltName, outDir,pltName)) 
htmlFile.write(' </body></html>\n')
htmlFile.close()
 
      
  
      
      
    
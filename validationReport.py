#!/bin/env python
import os
import sys
import re
import socket
import fileinput
import difflib

class tstSuite:
  
  def __init__(self,name):
    print 'Suite: ',name
    self.name    = name
    self.inpDir  = []
    self.outDir  = []
    self.prjList = []
    self.pltList = []
    
  def addPlt(self,pltName):
    self.pltList.append(pltName)

compName = socket.gethostname()

if compName == 'sm-bnc':
  testDir = 'D:\\TestHPAC' 
else:
  testDir = 'C:\\Users\\Bishusunita\\BNC\\TestSCICHEM'

regDir = 'b225x64'
outDir = '2014.10.09'  
  
scriptDir = os.path.join(testDir,'Scripts')
outputDir = os.path.join(testDir,'Outputs')

os.chdir(scriptDir)
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
        #print prjDir
    if "PlotList" in line:
      pltNames = line.split('=')[1].replace('${PlotList[@]}','').replace(';','').replace('(','').replace(')','').split()
      for pltName in pltNames:
        mySuite.addPlt(pltName)
    if "RptList" in line:
      pltNames = line.split('=')[1].replace('${RptList[@]}','').replace(';','').replace('(','').replace(')','').split()
      for pltName in pltNames:
        mySuite.addPlt(pltName)      
fileinput.close()
print

os.chdir(outputDir)

htmlFile = open('RegressionReport.html','w')
docType = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
docType += '<head><meta content="text/html; charset=ISO-8859-1" http-equiv="content-type"><title>Regression Test Results</title>\n'
docType += '  <style type="text/css"></style>\n'
docType += '  <link href="reports.css" type="text/css" rel="stylesheet" /></head>\n'
docType += ' <body>\n'
htmlFile.write(docType)

htmlDiff = difflib.HtmlDiff()
      
for suite in suiteList:
  
  htmlFile.write('<h1> Test Suite: ') 
  htmlFile.write(suite.name)
  htmlFile.write('</h1>\n') 

  print 'Suite: ',suite.name,'Plots: ',suite.pltList
  
  if 'Conflux' in suite.name:
     suite.pltList = ['cf_rp1', 'cf_rp2']
  
  for pltName in suite.pltList:
    
    
    if '.png' in pltName or '.' not in pltName:
      
      if '.png' not in pltName:
        pltName = pltName + '.png'
        
      if '_report' in pltName:
        regPlt = '%s/Reports/%s'%(regDir, pltName)
        outPlt = '%s/Reports/%s'%(outDir, pltName)
      else:
        regPlt = '%s/Plots/%s'%(regDir, pltName)
        outPlt = '%s/Plots/%s'%(outDir, pltName)
      
      if not os.path.exists(outPlt):
        if '/Plots/' in outPlt:
          regPlt = '%s/Reports/%s'%(regDir, pltName)
          outPlt = '%s/Reports/%s'%(outDir, pltName)
                
      if os.path.exists(outPlt):      
        print 'Add %s'%pltName  
        htmlFile.write('<Table><tr><td>') 
        htmlFile.write('<h3>Plot for version:%s<br></h3></td>'%regDir)
        htmlFile.write('<td><h3>Plot for version:%s<h3></td></tr>'%outDir)    
        htmlFile.write('<tr><td>')  
        htmlFile.write('<img  alt="%s Plot" src="%s">' %(regPlt,regPlt)) 
        htmlFile.write('</td><td>')  
        htmlFile.write('<img  alt="%s Plot" src="%s">' %(outPlt,outPlt)) 
        htmlFile.write('</td></tr></Table>\n')
        htmlFile.write('<footer></footer>\n') 
        #htmlFile.write('<hr/><footer></footer>\n')      
      else:
        print 'Missing %s'%outPlt
            
    else:    
              
      regFile = os.path.join(regDir,'Plots',pltName)
      outFile = os.path.join(outDir,'Plots',pltName)
      htmlFile.write('<p>Difference in %s for version:%s and %s<br>'%(pltName,regDir,outDir))
      print 'Difference in %s for version:%s and %s'%(pltName,regDir,outDir)
      diffLines = htmlDiff.make_table(open(regFile).readlines(), open(outFile).readlines(), fromdesc='', todesc='',\
                                context=False, numlines=2)
      htmlFile.write(diffLines)
  print

htmlFile.write(' </body></html>\n')
htmlFile.close()
 
      
  
      
      
    
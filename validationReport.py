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

# Date
htmlFile.write('<h1><small style="font-weight: normal; font-style: italic; color: rgb(255, 102, 0);"><small>')
htmlFile.write('Fri Oct 10 13:20:18 EDT 2014')
htmlFile.write('</small></small><br></h1>\n')

# Summary
htmlFile.write('<h1>Summary of regression test - <span style="color: rgb(255, 102, 0);">')
htmlFile.write('FAIL(0P,33F,33T)')
htmlFile.write('</span><br></h1>\n')

# Details

htmlFile.write('<h1 style="text-decoration: underline;">Details:</h1>\n')
htmlFile.write('<table><tr><td>')
htmlFile.write('<h2>Platform: ')
htmlFile.write('</td><td><h2> <span style="color: rgb(255, 102, 0);">')
htmlFile.write('Windows')
htmlFile.write('</span></h2>\n')
htmlFile.write('</td></tr>\n')

htmlFile.write('<tr><td>')
htmlFile.write('<h2>Current Executable Directory: ')
htmlFile.write('</td><td><h2><span style="color: rgb(255, 102, 0);">')
htmlFile.write('/cygdrive/d/SCIPUFF/2014-10-09/bin')
htmlFile.write('</span></h2>\n')
htmlFile.write('</td></tr>\n')

htmlFile.write('<tr><td>')
htmlFile.write('<h2>Regression Executable Directory: ')
htmlFile.write('</td><td><h2><span style="color: rgb(255, 102, 0);">')

htmlFile.write('/cygdrive/m/util256/amd64')
htmlFile.write('</span></h2>\n')
htmlFile.write('</td></tr></table>\n')
htmlFile.write('<footer></footer>\n') 

htmlFile.write('<h2>Regression Run Date &nbsp; <span style="color: rgb(255, 102, 0);">')
htmlFile.write('Wed Feb 12 16:09:07 EST 2014')
htmlFile.write('</span></h2>\n')

# Summary Table
htmlFile.write('<table style="text-align: left; width: 100%;" border="1" cellpadding="2" cellspacing="2">\n')
htmlFile.write('<tbody><tr><td style="width: 61px; text-align: center;">No.<br></td>\n')

htmlFile.write('<td style="width: 304px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;">')
htmlFile.write('Project Name<br></td>\n')

htmlFile.write('<td style="width: 87px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;">')
htmlFile.write('Results<br></td>\n')

htmlFile.write('<td style="width: 128px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;">')
htmlFile.write('Number of Puffs <br></td>\n')

htmlFile.write('<td style="width: 133px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;">')
htmlFile.write('Puff Dump<br></td>\n')

htmlFile.write('<td style="width: 360px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;">')
htmlFile.write('Dose Dump<br></td></tr>\n')

# Rows

for sunum,suite in enumerate(suiteList):
  htmlFile.write('<tr><td style="width: 61px; text-align: center;">')
  htmlFile.write('%s'%sunum)
  htmlFile.write('<br></td>')
  
  htmlFile.write('<td style="width: 304px; text-align: center;<h3>">')
  htmlFile.write('%s'%suite.name)
  htmlFile.write('</h3></td>\n')
  
  htmlFile.write('<td style="width: 87px; text-align: center;"><h3>')
  htmlFile.write('FAIL')
  htmlFile.write('</h3></td>\n')
  
  htmlFile.write('<td style="width: 128px; text-align: center;">')
  htmlFile.write('Different')
  htmlFile.write('<br></td>\n')
  
  htmlFile.write('<td style="width: 133px; text-align: center;">')
  htmlFile.write('Different')
  htmlFile.write('<br></td>\n')
  
  htmlFile.write('<td style="width: 360px; text-align: center;">')
  htmlFile.write('Different')
  htmlFile.write('<br></td></tr>\n')

htmlFile.write('</tbody></table>')

suiteProps = {}
for suite in suiteList:
  suiteProps.update({suite:['Using historical database','Fail']})

print 'suiteProps: ',suiteProps

htmlDiff = difflib.HtmlDiff()
      
for suite in suiteList:
  
  # Name
  htmlFile.write('<h1> <u>Test Suite: ') 
  htmlFile.write(suite.name)
  htmlFile.write('</u> </h1>\n') 
  
  # Purpose
  htmlFile.write('<h5><big><big>Purpose</big></big></h5>\n')
  htmlFile.write('<p class="MsoNormal">%s</p>\n'%suiteProps[suite][0])
  htmlFile.write('<h5><big><big>Regression : %s</big></big></h5>\n'%suiteProps[suite][1])
  htmlFile.write('<h5><big><big>Results: </big></big></h5>\n')
  
  print 'Suite: ',suite.name,', Plots:',suite.pltList
  
  if suite.name == 'SecondaryEvap':
    suite.pltList = ['SecondaryEvap1_01','SecondaryEvap1_02','SecondaryEvap2']
          
  if suite.name == 'ConfluxContinuous':
    suite.pltList = ['cf_rp1', 'cf_rp2']
     
  if suite.name == 'Etex':
    suite.pltList = ['etex', 'etexx_01'] 
  
  if suite.name == 'DataEtex':
    suite.pltList = ['etex.sta', 'plot_4', 'etexb', 'fig_etex']

  if suite.name == 'Instantaneous':
    suite.pltList = ['weil_report', 'mikkelsen_report', 'hogstrom_report']
    
  if suite.name == 'Jets':
    suite.pltList = ['jet_report1', 'jet_report2', 'bj_neutral_report', 'bj_stable_report']

  if suite.name == 'MultiMaterial':
    suite.pltList = ['MultiMaterial_01', 'MultiMaterial_02', 'MultiMateriala', 'MultiMaterialb', 'MultiMaterialc', 'MultiMateriald']          
  
  if suite.name == 'PGT':
    suite.pltList = ['PGT_report']
    
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
        htmlFile.write('<a href="%s" target="_blank">' %regPlt) 
        htmlFile.write('<img  alt="%s Plot" src="%s">' %(regPlt,regPlt)) 
        htmlFile.write('</a></td><td>')  
        htmlFile.write('<a href="%s" target="_blank">' %outPlt)  
        htmlFile.write('<img  alt="%s Plot" src="%s">' %(outPlt,outPlt)) 
        htmlFile.write('</a></td></tr></Table>\n')
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
 
      
  
      
      
    
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

# Current Output Directory
curDir     = os.getcwd()
baseDir    = os.path.dirname(curDir).replace('Outputs','')
outDir     = os.path.basename(curDir)
  
# Regression Directory
regDir     = sys.argv[1].replace('Outputs/','')  #'b225x64'
ReportFile = 'Regression_Test_Results_%s_%s.html'%(regDir,outDir)

# Make it relative to current directory
regDir     = os.path.join('..',regDir)

# Script Directory
scriptDir  = os.path.join(baseDir,'Scripts')

print 'Regression Dir = ',regDir
print 'Output Dir     = ',outDir
print 'Current Dir    = ',curDir
print 'ReportFile     = ',ReportFile,'\n'

suiteList = []
mySuite   = None
isCase    = False
for line in fileinput.input(os.path.join(scriptDir,'runlist.sh')):
  if "case" in line:
    isCase = True
    prjDir = None
    continue
  if "esac" in line:
    isCase = False
    break
  if isCase:
    if line.rstrip().endswith('")'):       
      mySuite = tstSuite(line.strip().replace(')','').replace('"',''))
      suiteList.append(mySuite)
    if "DIR=" in line:
      line  = line.strip().replace('"','').replace(';','')
      dName = line.split('=')[1].replace('${RUN}',suiteList[-1].name)
      if "INPDIR=" not in line and "OUTDIR=" not in line:
        prjDir = dName
        #print prjDir
    if "PlotList" in line:
      pltNames = line.split('=')[1].replace('${PlotList[@]}','').replace(';','').replace('(','').replace(')','').split()
      for pltName in pltNames:
        suiteList[-1].addPlt(pltName)
    if "RptList" in line:
      pltNames = line.split('=')[1].replace('${RptList[@]}','').replace(';','').replace('(','').replace(')','').split()
      for pltName in pltNames:
        suiteList[-1].addPlt(pltName)      
fileinput.close()
print

htmlFile = open(ReportFile,'w')
docType = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
docType += '<head><meta content="text/html; charset=ISO-8859-1" http-equiv="content-type"><title>Regression Test Results</title>\n'
htmlFile.write(docType)

if os.path.exists('reports.css'):
  #begin include style sheet file
  docType  = '  <style type="text/css"></style>\n'
  docType += '  <link href="reports.css" type="text/css" rel="stylesheet" />\n'
  docType += '</head>\n'
  docType += ' <body>\n'
  htmlFile.write(docType)
  #end include style sheet file
else:
  #begin inline style sheet
  styleType =  'html {\n'
  styleType += '  padding:35px 105px 0;\n'
  styleType += '  font-family:sans-serif;\n'
  styleType += '  font-size:14px;\n'
  styleType += '}\n'
  styleType += 'h1 {\n'
  styleType += '  margin-bottom:25px;\n'
  styleType += '}\n'
  styleType += 'p, h3 { \n'
  styleType += '  margin-bottom:15px;\n'
  styleType += '}\n'
  styleType += 'div {\n'
  styleType += '  padding:10px;\n'
  styleType += '  width:1200px;\n'
  styleType += '}\n'
  styleType += '.tabs li {\n'
  styleType += '  list-style:none;\n'
  styleType += '  display:inline;\n'
  styleType += '}\n'
  styleType += '.tabs a {\n'
  styleType += '  padding:5px 10px;\n'
  styleType += '  margin-bottom:8px;\n'
  styleType += '  display:inline-block;\n'
  styleType += '  background:#666;\n'
  styleType += '  color:#fff;\n'
  styleType += '  text-decoration:none;\n'
  styleType += '}\n'
  styleType += '.tabs a.active {\n'
  styleType += '  background:#fff;\n'
  styleType += '  color:#000;\n'
  styleType += '}\n'
  styleType += '?#tow { display: none; }?\n'
  styleType += 'div {\n'
  styleType += '  padding:10px;\n'
  styleType += '  width:1000px;\n'
  styleType += '  position: relative;\n'
  styleType += '  \n'
  styleType += '  left: 175px;\n'
  styleType += '}\n'
  styleType += 'img {\n'
  styleType += '  padding: 10px;\n'
  styleType += '  #//-webkit-box-shadow: 1px 1px 15px #999999;\n'
  styleType += '  box-shadow: 1px 1px 15px #999999;\n'
  styleType += '  height: 60%;\n'
  styleType += '  width: 60%;\n'
  styleType += '}\n'
  styleType += 'footer {\n'
  styleType += '  padding: 10px;\n'
  styleType += '}\n'
  styleType += 'media print {\n'
  styleType += '  footer {page-break-after: always;}\n'
  styleType += '}\n'

  htmlFile.write('<style>\n')
  htmlFile.write(styleType)
  htmlFile.write('</style>\n')

  htmlFile.write('</head>\n')
  htmlFile.write('<body>\n')
  #end style sheet

# Read Regression Summary Log
if os.path.exists('Regression_Summary.log'):
  regAvail = True
else:
  regAvail = False

if regAvail:
  summary   = {}
  runResult = {}
  runStatus = {}
  runName = None
  for line in fileinput.input('Regression_Summary.log'):
    if len(line.strip()) > 0:
      if 'RUN:' in line:
        # RUN:DTRAPhaseI,17,17,PRJ:r17m,CSO,CSR,DNP,NA,NA,FAIL
        runName = line.split(':')[1].split(',')[0].strip()
        rStat   = line.split(':')[2].split(',')[1:]
        if runName not in runStatus:
          stat = {'rNo':'','DNP':'','SNP':'','DPD':'','SPD':'','DDD':'','SDD':''}
          runStatus.update({runName:stat})
        if runStatus[runName]['rNo'] == '':
          runStatus[runName]['rNo'] = 0
        rNo = runStatus[runName]['rNo'] + 1
        stat.update({'rNo':rNo})
        nStat = {}
        for iStat,vStat in [[2,'DNP'],[2,'SNP'],[3,'DPD'],[3,'SPD'],[4,'DDD'],[4,'SDD']]:
          if rStat[iStat] == vStat:
            if runStatus[runName][vStat] == '':
              runStatus[runName][vStat] = 0
              nStat.update({vStat:0})
            nStat[vStat] = runStatus[runName][vStat] + 1
            stat.update({vStat:nStat[vStat]})
        runStatus.update({runName:stat})
        #if runName == 'DeardoffWillis':
        #  print line
        #  print runStatus[runName]
      elif 'Run Result' in line:
        # Run Result = FAIL(0P,17F,17T)
        runResult.update({runName:line.split('=')[1]})
        #if runName == 'DeardoffWillis':
        #  print line
        print '%s: %s'%(runName,runResult[runName])
        runName = None
      elif 'TestSummary' in line:
        testSummary = line.strip().split('=')[1]
      elif '=' in line:
        key,value = line.strip().split('=')
        summary.update({key.strip():value})

  '''
  for key in summary.iterkeys():    
    print 'key:',key.strip(),', value:',summary[key].strip()
  
  for runName in runStatus.iterkeys():    
    print 'runName:',runName,', Status:',runStatus[runName]

  for runName in runResult.iterkeys():    
    print 'runName:',runName,', Result:',runResult[runName]
  '''
  
# Details
# Date


htmlFile.write('<table>\n')

htmlFile.write('<tr><td><span style="font-weight: normal; font-style: italic; color: rgb(255, 102, 0);">')
htmlFile.write('%s'%summary['RunDate'])
htmlFile.write('</span><br></td><td></td></tr>\n')

if regAvail:
  # Summary
  htmlFile.write('<tr><td><h1>Summary of regression test : </h1></td> ')
  htmlFile.write('<td><h1><span style="color: rgb(255, 102, 0);">%s'%testSummary)
  htmlFile.write('</span><br></h1></td></tr>\n')

htmlFile.write('<tr><td><h1 style="text-decoration: underline;">Details:</h1></td><td></td></tr>\n')
htmlFile.write('<tr><td>')
htmlFile.write('<h2>Platform: ')
htmlFile.write('</td><td><h2> <span style="color: rgb(255, 102, 0);">')
htmlFile.write('%s'%summary['PLATFORM'])
htmlFile.write('</span></h2>\n')
htmlFile.write('</td></tr>\n')

htmlFile.write('<tr><td style="width: 504px; ">')#
htmlFile.write('<h2>Current Executable Directory: ')
htmlFile.write('</td><td><h2><span style="color: rgb(255, 102, 0);">')
htmlFile.write('%s'%summary['BINDIR'])
htmlFile.write('</span></h2>\n')
htmlFile.write('</td></tr>\n')

if regAvail:
  htmlFile.write('<tr><td>')
  htmlFile.write('<h2>Regression Executable Directory: ')
  htmlFile.write('</td><td><h2><span style="color: rgb(255, 102, 0);">')
  htmlFile.write('%s'%summary['RegBinDir'])
  htmlFile.write('</span></h2>\n')
  htmlFile.write('</td></tr>\n')

  htmlFile.write('<tr><td>')
  htmlFile.write('<h2>Regression Run Date:')
  htmlFile.write('</td><td><h2> <span style="color: rgb(255, 102, 0);">')
  htmlFile.write('%s'%summary['RegRunDate'])
  htmlFile.write('</span></h2>\n')
  htmlFile.write('</td></tr>\n')
htmlFile.write('</table>\n')
htmlFile.write('<footer></footer>\n') 

#
# Summary Table
#
# Headers
htmlFile.write('<table style="text-align: left; width: 100%;" border="1" cellpadding="2" cellspacing="2" >\n')
htmlFile.write('<tbody><tr><td rowspan=2 style="width: 60px; text-align: center; color: rgb(204, 102, 0); "><h1>No.</h1></td>\n')

htmlFile.write('<td rowspan=2 style="width: 160px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;">')
htmlFile.write('<h1>Project Name</h1></td>\n')

htmlFile.write('<td colspan=3 style="width: 90px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;">')
htmlFile.write('<h1>Results</h1></td>\n')

htmlFile.write('<td colspan=2 style="width: 128px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;">')
htmlFile.write('<h1>Number of Puffs </h1></td>\n')

htmlFile.write('<td colspan=2 style="width: 128px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;">')
htmlFile.write('<h1>Puff Dump</h1></td>\n')

htmlFile.write('<td colspan=2 style="width: 128px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;">')
htmlFile.write('<h1>Dose Dump</h1></td></tr>\n')

# Sub Columns
# Results
htmlFile.write('<tr>\n')
htmlFile.write('<td  style="width: 30px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;"><h1>Pass</h1></td>\n')
htmlFile.write('<td  style="width: 30px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;"><h1>Fail</h1></td>\n')
htmlFile.write('<td style="width: 30px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;"><h1>Total</h1></td>\n')
# No of Puffs
htmlFile.write('<td  style="width: 64px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;"><h1>Same</h1></td>\n')
htmlFile.write('<td  style="width: 64px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;"><h1>Different</h1></td>\n')
# Puff Dump
htmlFile.write('<td  style="width: 64px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;"><h1>Same</h1></td>\n')
htmlFile.write('<td  style="width: 64px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;"><h1>Different</h1></td>\n')
# Dose Dump
htmlFile.write('<td  style="width: 64px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;"><h1>Same</h1></td>\n')
htmlFile.write('<td  style="width: 64px; text-align: center; font-style: italic; color: rgb(204, 102, 0); font-weight: bold;"><h1>Different</h1></td>\n')
htmlFile.write('</tr>\n')

# Rows

for suNum,suite in enumerate(suiteList):
  htmlFile.write('<tr style="width: 64px; text-align: center;"><td style="width: 60px; text-align: center;">')
  htmlFile.write('%d'%(suNum+1))
  htmlFile.write('</td>')
  
  htmlFile.write('<td style="width: 160px; text-align: center;"><h3>')
  htmlFile.write('%s'%suite.name)
  htmlFile.write('</h3></td>\n')

  rResult = ''
  nResult = ['','','']
  stat    = {'rNo':'','DNP':'','SNP':'','DPD':'','SPD':'','DDD':'','SDD':''}
  print 
  if suite.name in runResult.iterkeys():
    if '(' in runResult[suite.name]:
      print 'Name:%s, runResult:%s'%(suite.name.strip(),runResult[suite.name].strip())
      rResult = runResult[suite.name].split('(')[0]
      nResult = runResult[suite.name].split('(')[1].split(')')[0].split(',')
      stat    = runStatus[suite.name]
  
  nPass   = nResult[0].replace('P','')
  nFail   = nResult[1].replace('F','')
  nTotal  = nResult[2].replace('T','')
  print suite.name.strip(),nResult
  print stat,'\n' #,nPass,nFail,nTotal
  

  htmlFile.write('<td style="width: 90px; text-align: center;">')
  htmlFile.write('%s</td><td>%s</td><td>%s</td>'%(nPass,nFail,nTotal))
  htmlFile.write('</td>\n')
  
  rNo  = str(stat['rNo'])
  nSNP = str(stat['SNP'])
  nDNP = str(stat['DNP'])
  
  # No. of puffs
  htmlFile.write('<td style="width: 64px; text-align: center;">')
  htmlFile.write('%s</td><td>%s</td>'%(nSNP,nDNP))
  
  # Puff Dump
  nSPD = str(stat['SPD'])
  nDPD = str(stat['DPD'])
  htmlFile.write('<td style="width: 64px; text-align: center;">')
  htmlFile.write('%s</td><td>%s</td>'%(nSPD,nDPD))
  
  # Dose Dump
  nSDD = str(stat['SDD'])
  nDDD = str(stat['DDD'])
  htmlFile.write('<td style="width: 64px; text-align: center;">')
  htmlFile.write('%s</td><td>%s</td>'%(nSDD,nDDD))
  htmlFile.write('</tr>\n')

htmlFile.write('</tbody></table>')
htmlFile.write('<footer></footer>')

suiteProps = {}
for suite in suiteList:
  #print suite.name
  suiteProps.update({suite.name:['','']})
  
suiteProps['3dClimatology'][0] = 'Using historical database' 
suiteProps['HillDense'][0] = 'Test dense gas on slope, quiescent background'
suiteProps['Hill'][0] = 'MC-SCIPUFF mass consistency model and plume interaction with idealized hill'
suiteProps['LSV'][0] = 'Large scale variability included in meteorology input.'
suiteProps['MultiMaterial'][0] = 'Dispersion tracking of several materials with different release specifications'
suiteProps['MultiProfile'][0] = 'Multiple meteorology observations'
suiteProps['SecondaryEvap'][0] = 'Secondary evaporation model'
suiteProps['LOSSampler'][0] = 'Line-of-sight samplers for obscurants'
suiteProps['RadSampler'][0] = 'Radiological samplers for RTH numerical decay materials'
suiteProps['NWPNSampler'][0] = 'Radiological samplers for NWPN analytic decay materials'
suiteProps['DepositionSampler'][0] = 'Deposition samplers'
suiteProps['AutoBySizeSampler'][0] = 'Dosage samplers on a by-size-group basis'
suiteProps['DTRAPhaseI'][0] = 'These tests contain multiple sequential puff releases to create ensemble statistics for probabilistic validation.'
suiteProps['RTH_NFAC'][0] = 'Dispersion with numerical decay of RTH radiological materials'
suiteProps['RTH_NWPN'][0] = 'Dispersion with numerical decay RTH radiological materials and analytic decay of NWPN materials'
suiteProps['NativeCoord'][0] = 'Reading gridded met data in native coordinate system'
suiteProps['SigmaCbyC'][0] = 'Test variations of C(sigma)/C(mean) for short range with different met conditions.  Stability varies from a-f, time averaging of 0s, 300s and 900s and large-scale meteorology types of none and model '
suiteProps['BuoyantPuff'][0] = 'Centroid height and surface concentration for light bubbles released into a boundary layer with idealized free convection profiles'
suiteProps['ColdBubble'][0] = 'Comparison between calculated mean bubble rise and spread with measurements for instantaneous buoyant releases. Meteorology: quiescent background'
suiteProps['ConfluxContinuous'][0] = 'Compare vertical profiles of mean concentration and standard deviation to concentration time series constructed from measurements of neutrally buoyant plumes in slightly convective to moderately stable atmospheric conditions'
suiteProps['DeardoffWillis'][0] = 'Continuous buoyant releases in a capped convective boundary layer'
suiteProps['Etex'][0] = 'Long range diffusion of passive tracer across Europe'
suiteProps['FackrellRobins'][0] = 'Concentration fluctuations'
suiteProps['Instantaneous'][0] = 'Using historical database'
suiteProps['Jets'][0] = 'Jet centerline height as a function of downstream distance for a variety of exit velocity ratios'
suiteProps['PGT'][0] = 'Short range dispersion from surface release'
suiteProps['Spore'][0] = 'Dispersion of spores released from an elevated line source within a wheat canopy'
suiteProps['DataEtex'][0] = 'Long range diffusion of passive tracer across Europe'
suiteProps['MDAPassive'][0] = 'Dispersion of a passive gas'
suiteProps['MDADense'][0] = 'Dispersion of a passive dense gas'
suiteProps['MDASigmax'][0] = 'Dispersion of a passive light gas'
suiteProps['EPRI'][0] = 'Mid range diffusion of a passive tracer in both flat and complex terrain environments'

#print 'suiteProps: ',suiteProps
#suiteProps['Anatex'][0] = 'Long range diffusion of passive tracer across North America'
#print 'suiteProps: ',suiteProps
#sys.exit()

htmlDiff = difflib.HtmlDiff()
      
for suNum,suite in enumerate(suiteList):  
    
  # Name
  htmlFile.write('<h1><u> %d. Test Suite: '%(suNum+1)) 
  htmlFile.write(suite.name)
  htmlFile.write('</u> </h1>\n') 
  
  # Purpose
  htmlFile.write('<h5><big><big>Purpose</big></big></h5>\n')
  htmlFile.write('<p class="MsoNormal">%s</p>\n'%suiteProps[suite.name][0])
  htmlFile.write('<h5><big><big>Regression : %s</big></big></h5>\n'%suiteProps[suite.name][1])
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

  if suite.name == 'NativeCoord':
    suite.pltList = ['NativeCoord']
  
  #if suite.name == 'AutoBySizeSampler':
  #  suite.pltList = ['AutoBySizeSampler.smp']
    
  if suite.name == 'LOSSampler':
    suite.pltList = ['LOSSampler']
 
  if suite.name == 'LOSSampler':
    suite.pltList = ['LOSSampler']
  
  if suite.name == 'DepositionSampler':
    suite.pltList = ['DepositionSampler1','DepositionSampler2']

  if suite.name == 'NWPNSampler':
    suite.pltList = ['NWPNSampler1','NWPNSampler2']

  if suite.name == 'RadSampler':
    suite.pltList = ['RadSampler1','RadSampler2','RadSampler3']

  if suite.name == 'RTH_NFAC':
    suite.pltList = ['RTH_NFAC1','RTH_NFAC2','RTH_NFAC3']

  if suite.name == 'RTH_NWPN':
    suite.pltList = ['RTH_NWPN1','RTH_NWPN2','RTH_NWPN3']
      
  if suite.name == 'RadSampler':
    suite.pltList = ['RadSampler1','RadSampler2','RadSampler3']

  if suite.name == 'SigmaCbyC':
    suite.pltList = ['CCOC00.out','CCOC01.out','CCOC30.out','CCOC31.out','CCOC90.out','CCOC91.out']
       
  for pltName in suite.pltList:    
    
    if '.png' in pltName or '.' not in pltName:
      
      if '.png' not in pltName:
        pltName = pltName + '.png'
        
      if '_report' in pltName:
        regPlt = '%s/Reports/%s'%(regDir, pltName)
        outPlt = 'Reports/%s'%(pltName)
      else:
        regPlt = '%s/Plots/%s'%(regDir, pltName)
        outPlt = 'Plots/%s'%(pltName)
      
      if not os.path.exists(outPlt):
        if 'Plots/' in outPlt:
          regPlt = '%s/Reports/%s'%(regDir, pltName)
          outPlt = 'Reports/%s'%(pltName)
                
      if os.path.exists(outPlt):      
        if os.path.exists(regPlt):      
          print 'Add %s'%pltName  
          htmlFile.write('<Table><tr><td>') 
          htmlFile.write('<h3>Plot for version:%s<br></h3></td>'%os.path.basename(regDir))
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
          print('Missing %s for version:%s'%(pltName,regDir))
          htmlFile.write('<p>Missing %s for version:%s</p><br>'%(pltName,regDir))
      else:
        print('Missing %s for version:%s'%(pltName,outDir))
        htmlFile.write('<p>Missing %s for version:%s</p><br>'%(pltName,outDir))
            
    else:    
              
      regFile = os.path.join(regDir,'Plots',pltName)
      outFile = os.path.join('Plots',pltName)
      if os.path.exists(regFile):
        if os.path.exists(outFile):
          diffLines = htmlDiff.make_table(open(regFile).readlines(), open(outFile).readlines(), fromdesc='', todesc='',\
                                context=False, numlines=2)
          htmlFile.write('<p>Difference in %s for version:%s and %s</p><br>'%(pltName,regDir,outDir))
          print 'Difference in %s for version:%s and %s'%(pltName,regDir,outDir)
          htmlFile.write(diffLines)
        else:
          htmlFile.write('<p>Missing %s for version:%s</p><br>'%(pltName,outDir))
          print 'Missing %s'%outFile
      else:
        htmlFile.write('<p>Missing %s for version:%s</p><br>'%(pltName,regDir))
        print 'Missing %s'%regFile
  print

htmlFile.write(' </body></html>\n')
htmlFile.close()
print 'Completed creating html report file %s in %s\n'%(ReportFile,os.getcwd())

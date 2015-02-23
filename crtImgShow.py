#!/bin/env python
import os
import sys
import re
import socket
import fileinput

# Current Output Directory
curDir     = os.getcwd()
regDir     = 'dyn'
outDir     = 'prise'
ReportFile = 'Compare_%s_%s.html'%(regDir,outDir)

print 'Regression Dir = ',regDir
print 'Output Dir     = ',outDir
print 'Current Dir    = ',curDir
print 'ReportFile     = ',ReportFile,'\n'

os.chdir(outDir)
pltList = os.listdir('./')
print pltList
regDir  = os.path.join('..',regDir)  

htmlFile = open(ReportFile,'w')
docType = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
docType += '<head><meta content="text/html; charset=ISO-8859-1" http-equiv="content-type"><title>Regression Test Results</title>\n'
htmlFile.write(docType)

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

       
for pltName in pltList:    
  
  if '.png' in pltName or '.' not in pltName:

    if '.png' not in pltName:
      pltName = pltName + '.png'
      
    regPlt = '%s/%s'%(regDir, pltName)
    outPlt = '%s'%(pltName)
    if os.path.exists(outPlt):      
      if os.path.exists(regPlt):      
        print 'Add %s'%pltName  
        htmlFile.write('<Table><tr><td>') 
        htmlFile.write('<h3>%s(%s)<br></h3></td>'%(pltName,os.path.basename(regDir)))
        htmlFile.write('<td><h3>%s(%s)<h3></td></tr>'%(pltName,outDir))
        htmlFile.write('<tr><td>')  
        htmlFile.write('<a href="%s" target="_blank">' %regPlt) 
        htmlFile.write('<img  alt="%s Plot" src="%s">' %(regPlt,regPlt)) 
        htmlFile.write('</a></td><td>')  
        htmlFile.write('<a href="%s" target="_blank">' %outPlt)  
        htmlFile.write('<img  alt="%s Plot" src="%s">' %(outPlt,outPlt)) 
        htmlFile.write('</a></td></tr></Table>\n')
        htmlFile.write('<footer></footer>\n') 
      else:
        print('Missing %s for version:%s'%(pltName,regDir))
        htmlFile.write('<p>Missing %s for version:%s</p><br>'%(pltName,regDir))
    else:
      print('Missing %s for version:%s'%(pltName,outDir))
      htmlFile.write('<p>Missing %s for version:%s</p><br>'%(pltName,outDir))
            
  else:    
            
    regFile = os.path.join(regDir,pltName)
    outFile = pltName
    if os.path.exists(regFile):
      if os.path.exists(outFile):
        diffLines = htmlDiff.make_table(open(regFile).readlines(), open(outFile).readlines(), fromdesc='', todesc='',\
                              context=False, numlines=2)
        htmlFile.write('<p>Difference in %s for version:%s and %s</p><br>'%(pltName,regDir,outDir))
        print 'Difference in %s for version:%s and %s'%(pltName,regDir,outDir)
        htmlFile.write(diffLines)
      else:
        #htmlFile.write('<p>Missing %s for version:%s</p><br>'%(pltName,outDir))
        print 'Missing %s'%outFile
    else:
      #htmlFile.write('<p>Missing %s for version:%s</p><br>'%(pltName,regDir))
      print 'Missing %s'%regFile

  print

htmlFile.write(' </body></html>\n')
htmlFile.close()
print 'Completed creating html report file %s in %s\n'%(ReportFile,os.getcwd())

os.chdir(curDir)

#!/bin/env python
import os
import sys
import re
import socket
import fileinput

# Current Output Directory
curDir     = os.getcwd()
ReportFile = 'Compare_Plots.html'

print 'Current Dir    = ',curDir

os.chdir('C:\\Users\\sid\\Dropbox\\SUBI\\cmpDir')
#os.chdir('C:\\Users\\Bishusunita\\Dropbox\\SUBI\\cmpDir')
print 'ReportFile     = ',ReportFile,'\n'

pltList = os.listdir('./')

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
styleType += '  height: 90%;\n'
styleType += '  width: 90%;\n'
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

# Arrange according to keywords
keyNames = ['20km','55km','110km']

for keyName in keyNames:
  
  print keyName
  
  pltNames = []
  for pltName in pltList:    
    if '%s.png'%keyName in pltName:
      pltNames.append(pltName)    
  print pltNames

  htmlFile.write('\n<Table>\n<tr><td>') 
  htmlFile.write('<h3>%s<br></h3></td></tr>\n'%keyName)  
  for i in range(0,len(pltNames),2):
    print 'Add %s'%pltNames[i]  
    htmlFile.write('\n<tr><td>')  
    htmlFile.write('<a href="%s" target="_blank">' %pltNames[i]) 
    htmlFile.write('<img  alt="%s Plot" src="%s">' %(pltNames[i],pltNames[i])) 
    if i+1 < len(pltNames):
      htmlFile.write('</a></td>\n  <td>')
      print 'Add %s'%pltNames[i+1]    
      htmlFile.write('<a href="%s" target="_blank">' %pltNames[i+1])  
      htmlFile.write('<img  alt="%s Plot" src="%s">' %(pltNames[i+1],pltNames[i+1])) 
    htmlFile.write('</a></td> </tr>\n')
  htmlFile.write('\n<footer></footer>\n') # To keep each plot on separate page
  htmlFile.write('</Table>\n')             
  print

htmlFile.write(' </body></html>\n')
htmlFile.close()
print 'Completed creating html report file %s in %s\n'%(ReportFile,os.getcwd())


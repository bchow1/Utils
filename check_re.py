#!/usr/bin/python
import os
import sys
import re
import fileinput

inFile = 'OLAD_S251.msc'
#inFile = 'Fwd048_Predict.inp'
#inFile = 'Fwd048_Actual.inp'
#inFile = '../../Fwdxxx.inp'
#inpNml = ['matdef','options']
inpNml = ['options']
endNml = '/'
for nml in inpNml:
  #Cpattern = '\s*&%s\s*'%nml
  #pattKey  = re.compile(Cpattern,re.I)
  #pattKey  = re.compile("(.*SMPFILE\s*=\s*)(.*?)(\s*,|$.*)",re.I)
  #pattKey = re.compile("(HPAC)|(SCIPUFF)\s*",re.I)
  #pattKey = re.compile("(.*@)(\d{3}.+)(\s*.*)")
  pattKey  = re.compile(r".*\b(zb\s*=\s*)(.*?)($)",re.I)
  
  for line in fileinput.input(inFile):
    print 'line: ',line.strip()
    matchKey = pattKey.match(line)
    if matchKey:
      print 'FOUND MATCH'
      line = matchKey.group(1) + 'SUBSTITUTE' + matchKey.group(3)
      #line = matchKey.group(2)
      print 'new line: ',line
      #break
  fileinput.close()

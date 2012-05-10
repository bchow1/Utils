#!/bin/python
import os
import sys
import re
import fileinput

if len(sys.argv) != 2 :
  print('Usage: matchFpp file')


ifStart = re.compile("!DEC\$ IF DEFINED\s*\(.+")
ifElif  = re.compile("!DEC\$ ELSEIF\s+.+")
ifElse  = re.compile("!DEC\$ ELSE.*")
ifEnd   = re.compile("!DEC\$ ENDIF.*")

#fName = sys.argv[1]
fName = 'D:\\hpac\\gitEPRI\\src\\lib\\SCIPUFFlib\\SCIPUFF\\initial.f90'

nlev = 0
spaces = ''
for line in fileinput.input(fName):
  matchStart = ifStart.match(line)
  matchElse  = ifElse.match(line)
  matchEnd   = ifEnd.match(line)
  #print fileinput.lineno(),':',line
  lNo = '%04d:'%fileinput.lineno()
  if matchStart or matchElse:
    if matchStart:
      nlev += 1 
      heads = spaces + '|-'
      spaces = spaces + '| '
    sys.stdout.write('%s%s%s'%(lNo,heads,line))
  elif matchEnd:
    sys.stdout.write('%s%s%s'%(lNo,heads,line))
    nlev -= 1 
    heads = heads[:-3] + '-'
    spaces = spaces[:-2]
  else:
    sys.stdout.write('%s%s%s'%(lNo,spaces,line))
  


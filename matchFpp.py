#!/usr/bin/python
import os
import sys
import re
import fileinput

#if len(sys.argv) != 2 :
#  print('Usage: matchFpp file')

isFlush = True
#isFlush = False
#prntLNo = True
prntLNo = False
 
if isFlush: 
  bChar =""
else:
  bChar =".+"

ifStart = re.compile(bChar+"!DEC\$ IF DEFINED\s*\(.+")
ifStarn = re.compile(bChar+"!DEC\$ IF \.NOT\.\s*DEFINED\s*\(.+")
ifElif  = re.compile(bChar+"!DEC\$ ELSEIF\s+.+")
ifElse  = re.compile(bChar+"!DEC\$ ELSE.*")
ifEnd   = re.compile(bChar+"!DEC\$ ENDIF.*")

fName = sys.argv[1]
#fName = 'D:\\SCIPUFF\\OMP_WIP\\src\\dll\\SCIPUFFlib\\SCIPUFF\\step.f90'
#fName  = 'D:\\SCIPUFF\\OMP_WIP\\src\\lib\\SCIPUFFlib\\SCIPUFF\\util_puff.f90'

nlev = 0
spaces = ''
for line in fileinput.input(fName):
  matchStart = ifStart.match(line)
  matchStarn = ifStarn.match(line)
  matchElse  = ifElse.match(line)
  matchEnd   = ifEnd.match(line)
  #print fileinput.lineno(),':',line
  #print matchStart
  lNo = '%04d:'%fileinput.lineno()
  lNo = '%04d:'%fileinput.lineno()
  if matchStart or matchStarn:
    nlev += 1 
    heads  = spaces + '{-'
    mids   = spaces + '|='
    tails  = spaces + '}-'
    spaces = spaces + '| '
    if prntLNo:
      sys.stdout.write('%s%s%s'%(lNo,heads,line))
    else:
      sys.stdout.write('%s%s'%(heads,line))
  elif matchElse:
    if prntLNo:
      sys.stdout.write('%s%s%s'%(lNo,mids,line))
    else:
      sys.stdout.write('%s%s'%(mids,line))    
  elif matchEnd:
    if prntLNo:
      sys.stdout.write('%s%s%s'%(lNo,tails,line))
    else:
      sys.stdout.write('%s%s'%(tails,line))
    nlev -= 1 
    heads  = heads[:-3] + '-'
    mids   = mids[:-3]  + '-'
    tails  = tails[2:]
    spaces = spaces[:-2]
  else:
    if prntLNo:
      sys.stdout.write('%s%s%s'%(lNo,spaces,line))
    else:
      sys.stdout.write('%s%s'%(spaces,line))
  

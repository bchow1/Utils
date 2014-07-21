#!/bin/python

import os
import sys
import optparse

# Parse arguments
arg = optparse.OptionParser()
arg.add_option("-n",action="store",type="choice",choices=["yes","no"],dest="dryrun")
arg.add_option("-k",action="store",type="string",dest="keyword")
arg.add_option("-s",action="store",type="string",dest="suffix")
arg.add_option("-p",action="store",type="string",dest="prefix")

arg.set_defaults(dryrun="yes",keyword=None,suffix=None,prefix=None)
opt,args = arg.parse_args()

if opt.keyword is None and opt.suffix is None and opt.prefix is None:
  print 'Error: keyword, suffix or prefix must be specified'
  print 'Usage: reName.py [-k oldkeyword:newkeyword -s oldsuffix:newsuffix -p oldprefix:newprefix]'
  sys.exit()

if opt.dryrun.lower() == 'no':
  lDry = False
else:
  lDry = True

if opt.keyword is not None:
  lKey  = True
  kValo,kValn = opt.keyword.split(':')
else:
  lKey = False

if opt.suffix is not None:
  lSuf = True
  sValo,sValn = opt.suffix.split(':')
else:
  lSuf = False

if opt.prefix is not None:
  lPre = True
  pValo,pValn = opt.prefix.split(':')
else:
  lPre = False

fList = os.listdir("./")

for fName in fList:

  lAdd = False
  nName = 'NOT_SET'
  
  if lKey:
    if kValo in fName:
      lAdd = True 
      nName = fName.replace(kValo,kValn)
  if lSuf:
    if fName.endswith(sValo):
      lAdd = True 
      nName = fName.replace(sValo,sValn)
  if lPre:
    if fName.startswith(pValo):
      lAdd = True 
      nName = fName.replace(pValo,pValn)

  if lAdd:
    if not lDry:
      print 'Renaming %s -> %s'%(fName,nName)
      os.rename(fName,nName)
    else:
      print 'Dryrun: Renaming %s -> %s'%(fName,nName)

  

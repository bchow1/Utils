#!/bin/python
import os
import sys
import re
import shutil

import run_cmd

if sys.argv.__len__() < 3:
  print "Usage diffr.py file1 file2 [sfx/ALL [lh]]"
  sys.exit()

file1 = sys.argv[1]
file2 = sys.argv[2]

f1=os.path.basename(file1)
d1=os.path.dirname(file1)
if d1 == "": 
  d1 = "."
f2=os.path.basename(file2)
d2=os.path.dirname(file2)
if d2 == "": 
  d2 = "."


sfxList = ['.inp','.msc','.scn']
   
getList = False
if sys.argv.__len__() > 2:
  if sys.argv.__len__() == 3:
    getList = True
  elif sys.argv[3] == 'ALL':
    getList = True
  else:
    sfxList = sys.argv[3].split(':')
    for sfx in sfxList:
      f = os.path.join(d1,'%s.%s'%(f1,sfx))
      if not os.path.exists(f):
        print 'Error cannot find ',f
        sys.exit()
  if getList:
    sfxList = []
    fileList = os.listdir(d1)
    for f in fileList:
      if f.startswith(f1):
        sfx = f.split('.')[-1]
        sfxList.append(sfx)

def subLh(fName,fl,sfx):
  tmpfl = None
  fIn  = open(fName,'r')
  sngl = False
  for line in fIn:
    if line.strip().startswith(r'&') and line.strip().endswith(r'/'):
      sngl = True
      break
  fIn.seek(0)
  if sngl:
    fOut = open('temp_%s.%s'%(fl,sfx),'w')
    for line in fIn:
      lsplit = line.split(',')
      nsplit = len(lsplit)
      print 'lsplit len, last = ',nsplit,lsplit[-1]
      for lno,nline in enumerate(lsplit):
        if nline.strip().startswith('&'):
          nline = re.sub(r'\s*&(.+)\s+(.+)',r'&\1\n\2,',nline).strip()
        if nline.strip().endswith(r'/'):
          nmlEnd = True
          nline = re.sub(r'/\s*\n',r',\n/\n',nline).strip()
          fOut.write('%s\n'%nline)
        else:
          nmlEnd = False
        if lno < nsplit-1:
          print 'lno = ',lno,nsplit-1
          if (not nmlEnd) and ('=' in lsplit[lno+1]):
            fOut.write('%s,\n'%nline)
          else:
            fOut.write('%s,'%nline)
          fOut.write('%s,'%nline)
        else:
          fOut.write('%s,\n'%nline)
    fOut.close()
    tmpfl = 'temp_%s.%s'%(fl,sfx)
  fIn.close()
  return tmpfl
  
env = os.environ.copy()
for sfx in sfxList:
  fl1 = os.path.join(d1,'%s.%s'%(f1,sfx))
  fl2 = os.path.join(d2,'%s.%s'%(f2,sfx))
  tmpfl = subLh(fl1,f1,sfx)
  if tmpfl is not None:
    fl1 = tmpfl
  tmpfl = subLh(fl2,f2,sfx)
  sys.exit()
  if tmpfl is not None:
    fl2 = tmpfl
  cmd = ['diff','-i','-w','-b','%s'%fl1,'%s'%fl2]
  run_cmd.Command(env,cmd,'','\n',errOut=False,outOut=True)
  #if fl1.startswith('temp_'):
    #shutil.move(fl1,os.path.join(d1,'%s.%s'%(f1,sfx)))
  #if fl2.startswith('temp_'):
    #os.remove(fl2,os.path.join(d1,'%s.%s'%(f2,sfx)))

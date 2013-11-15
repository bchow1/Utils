#!/usr/bin/env /usr/bin/python
import os
import sys
import subprocess

def find_key(dic, val):
  """return the key of dictionary dic given the value"""
  return [k for k, v in dic.iteritems() if v == val][0]

def Command(env,cmd,Inputs,tail,errOut=True,outOut=False):
  ''' Function to run any system command with Inputs read on multiple lines. 
      Must set env and tail. If errors are generated, print error and return
      IOstat = -1 otherwise return the Outputs. '''
  print 'Running ',cmd,'...'
  
  if env is None:
    env = os.environ.copy()

   
  if sys.platform == 'win32':
    if tail is None:
      tail = '\r\n'
    h = subprocess.Popen(cmd, env=env, bufsize=0, shell=False,
                       stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
  else:
    if tail is None:
      tail = '\n'
    h = subprocess.Popen(cmd, env=env, bufsize=0, shell=False,
                       stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, close_fds=True)
  (Outputs, Errors) = h.communicate(input=Inputs)
  h.wait()
  
  lines = Errors.split(tail)
  
  if False: # len(lines) > 1:
    IOstat = -1
  else:
    IOstat = 0
    
  if errOut:
    print ('   ****Errors from %s *****'%cmd)
    for line in lines:
      print line
    print ('   ***************')
  
  lines = Outputs.split(tail)  
  if outOut:
      print ('   ****Output from %s *****'%cmd)
      for line in lines:
        print line
      print ('   ***************')
  
  return(Outputs,IOstat)

def hms2hr(HHMMSS):
  try:
    (HH, MM, SS) = HHMMSS.split(':')
  except ValueError:
    try:
      (HH, MM) = HHMMSS.split(':')
      SS       = 0.
    except ValueError:
      try:
        HH = float(HHMMSS)
        MM = 0.
        SS = 0. 
      except ValueError:
        HH = None
  if HH:
    hr = float(HH) + float(MM)/60. + float(SS)/3600.
  else:
    hr = None
  return hr

def hr2hms(hr):
  try:
    HH = int(hr)
  except ValueError:
    HH = -999
  if HH != -999: 
    MM  = int((hr-HH)*60.)
    SS  = int(round((hr-HH)*3600. - MM*60.))
    hms = "%02d:%02d:%02d"%(HH,MM,SS)
  else:
    hms = None
  return hms

# Main program for testing

if __name__ == '__main__':
  #cmd = "";
  #if sys.argv.__len__() > 1:
  #  cmd = sys.argv[1]
  #else:
  #  print 'Usage: run_cmd.py Command Inputs...\n'
  #  sys.exit(1)
 
  env = os.environ.copy()
  if sys.platform == 'win32':
    SCIPUFF_BASEDIR="d:\hpac\repository\bin\Release"
    OldPath = env["PATH"]
    env["PATH"] = "%s;%s" % (OldPath,SCIPUFF_BASEDIR)
    tail = '\r\n'
  else:
    SCIPUFF_BASEDIR="/home/user/bnc/hpac/repository/bin/linux/lahey"
    env["SCIPUFF_BASEDIR"] = SCIPUFF_BASEDIR
    env["LD_LIBRARY_PATH"] = "/usr/local/lf9561/lib:%s" % SCIPUFF_BASEDIR
    tail = '\n'
   
  #Inputs = "";
  #if sys.argv.__len__() > 2:
  #  for i in range(2, sys.argv.__len__()):
  #    Inputs = Inputs + ('%s'%(sys.argv[i] + tail));
  #print Inputs
  #(Outputs,IOstat) = Command(env,cmd,Inputs,tail)
  #print 'IOstat = ',IOstat
  #print 'Outputs:\n',Outputs.split(tail)
 
  print 'Test hms2hr'
  hr = hms2hr('10:11:13')
  print hr
  print hr2hms(hr)
  hr = hms2hr('10:11')
  print hr
  print hr2hms(hr)
  hr = hms2hr('10')
  print hr
  print hr2hms(hr)
  hr = hms2hr('today')
  print hr
  print hr2hms(hr)

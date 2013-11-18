import os
import sys
import optparse

#
import run_cmd

def printDiff(rev1,rev2):
  cmd = ['C:/cygwin/bin/cvs.exe','diff','-r1.%d'%rev1,'-r1.%d'%rev2,'%s'%fName]
  (Outputs,IOstat) = run_cmd.Command(env,cmd,(''),tail,errOut=False,outOut=True)
  lines = Outputs.split('\n')
  for line in lines:
    print line
    
# Parse arguments
arg = optparse.OptionParser()
arg.add_option("-f",action="store",type="string",dest="fileName")
arg.add_option("-s",action="store",type="string",dest="startRev")
arg.add_option("-e",action="store",type="string",dest="endRev")
arg.set_defaults(fileName=None,startRev=None,endRev=None)
opt,args = arg.parse_args()
# Check arguments
if opt.fileName is None:
  print 'Error: fileName must be specified'
  if sys.platform == 'win32':
    print 'Usage: runpy.sh ~/python/cvs_diff.py -f fileName [-s startRev] [ -e endRev]'
  else:
    print 'Usage: cvs_diff.py -f fileName [-s startRev] [ -e endRev]'
  print '       startRev can be -tive'
else:
  env = os.environ.copy()
  if sys.platform == 'win32':
    cygPath="C:\\cygwin\\bin"
    oldPath = env["PATH"]
    env["PATH"] = "%s;%s" % (cygPath,oldPath)
    env["CVS_RSH"] = "ssh"
    tail = '\r\n'
    SSH_AGENT_PID = None
    (Outputs,IOstat) = run_cmd.Command(env,['C:/cygwin/bin/printenv'],(''),tail,errOut=False)
    lines = Outputs.split('\n')
    for line in lines:
      if line.strip().startswith('SSH_AGENT_PID'):
        SSH_AGENT_PID = line.strip().split('=')[1].strip()
      if line.strip().startswith('SSH_AUTH_SOCK'):
        SSH_AUTH_SOCK = line.strip().split('=')[1].strip()
    if SSH_AGENT_PID is None:
      print 'Start ssh-agent before running cvs_diff.py'
      sys.exit()
    else:
      env['SSH_AGENT_PID'] = SSH_AGENT_PID
      env['SSH_AUTH_SOCK'] = SSH_AUTH_SOCK
    print env['SSH_AGENT_PID']
    print env['SSH_AUTH_SOCK']
  else:
    tail = '\n'
  
  # Get working and repository versions
  dName    = os.path.dirname(opt.fileName)
  fName    = os.path.basename(opt.fileName)
  startRev = opt.startRev
  endRev   = opt.endRev
  cDir = os.getcwd()
  dName = os.path.join(cDir,dName)
  os.chdir(dName)
  
  (Outputs,IOstat) = run_cmd.Command(env,['C:/cygwin/bin/cvs.exe','status','%s'%fName],(''),tail,errOut=False)
  lines = Outputs.split('\n')
  for line in lines:
    if line.strip().startswith('Working revision'):
      wrkRev = int(line.strip().split(':')[1].strip().split('.')[1])
      print 'wrkRev:',wrkRev
    if line.strip().startswith('Repository revision'):
      repRev = int(line.strip().split(':')[1].split()[0].strip().split('.')[1])
      print 'repRev:',repRev

  if endRev is None:
    endRev = repRev

  if startRev is None:
    if wrkRev < repRev:
      printDiff(wrkRev,repRev)
    else:
      printDiff(repRev,wrkRev)
    startRev = 1
  else:
    startRev = int(startRev)
    if startRev < 0:
      startRev = endRev + startRev
  
  print type(endRev),type(startRev)
  for iver in range(endRev,startRev,-1):
    print '\nVersion: ',iver
    printDiff(iver-1,iver)



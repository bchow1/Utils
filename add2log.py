#
import os
import sys
import optparse
import fileinput

# This program adds sampler locations in samfile to the logfile
def readSam(samFile):
  xySam = []
  for line in fileinput.input(samFile):
    if fileinput.lineno() == 1:
      continue
    x,y = map(float,line.strip().split()[:2])
    if [x,y] not in xySam:
      xySam.append([x,y])
  fileinput.close()
  return xySam

def wrtLog(logName,xySam):
  
  logFile = open(logName,"r")
  tmpFile = open(logName + '.tmp',"w")
  isAdded = False
  
  for line in logFile:
    # look for nzBL
    #if ($line =~ /^Computational domain/i && $Added eq "NOTSET"  ){
    tmpFile.write('%s'%line)
    if 'nzBL' in line and not isAdded:
      print "Adding after line: ",line
      # Add the additional lines 
      tmpFile.write("**************\n")
      tmpFile.write("***Samplers***\n")
      tmpFile.write("**************\n")   
      tmpFile.write("&wxsloc\n")
      tmpFile.write('wx = "SFC"\n')
      tmpFile.write('nwx = %d\n'%len(xySam))
      for nSam,xy in enumerate(xySam):
        tmpFile.write('xwx(%d)  = %12.4f, ywx(%d) = %12.4f\n'%(nSam+1,xy[0],nSam+1,xy[1]))
      tmpFile.write('/\n')
      isAdded = True
  tmpFile.close()
  logFile.close()
  
# Call main program
if __name__ == '__main__':
  os.chdir('d:\\SCIPUFF\\EPRIx\\SCICHEM-2012\\runs\\tva\\tva_990715')
  # Parse arguments
  arg = optparse.OptionParser()
  arg.add_option("-l",action="store",type="string",dest="logFile")
  arg.add_option("-s",action="store",type="string",dest="samFile")
  arg.set_defaults(logFile=None,samFile=None)
  opt,args = arg.parse_args()

  if opt.logFile is None and opt.samFile is None:
    print 'Error: logFile and samFile must be specified'
    print 'Usage: add2log.py [-l logFile -s samFile]'
    sys.exit()

  if not os.path.exists(opt.logFile):
    print 'Error: Cannot file log file ',opt.logFile

  if not os.path.exists(opt.samFile):
    print 'Error: Cannot file sam file ',opt.samFile
         
  xySam = readSam(opt.samFile)
  print xySam
  
  if len(xySam) > 0:
    wrtLog(opt.logFile,xySam)
  
  print 'Done'
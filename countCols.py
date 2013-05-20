#

import sys
import os
import fileinput
import optparse

print os.getcwd()


# Call main program
if __name__ == '__main__':
  
  os.chdir('d:\\SCIPUFF\\EPRI\\runs\\negativeO3\\SCICHEM-ROME')
  
  # Parse arguments
  arg = optparse.OptionParser()
  arg.add_option("-l",action="store",type="int",dest="lineNo")
  arg.add_option("-f",action="store",type="string",dest="fileName")
  arg.add_option("-k",action="store",type="string",dest="keyWord")
  arg.add_option("-s",action="store",type="string",dest="separator")
  arg.set_defaults(lineNo=1,fileName=None,keyWord=None,separator=None)
  opt,args = arg.parse_args()

  if opt.keyWord is None:
    keyWord = None
    if opt.lineNo is None:
      lineNo = 1
    else:
      lineNo = int(opt.lineNo)
  else:
    keyWord = opt.keyWord
    lineNo  = None
    
  sptr = opt.separator

  if opt.fileName is None :
    print 'Error: File name must be specified'
    print 'Usage: countCols.py -f fileName [-l lineNo] [-k keyWord] [-s separator]'
    sys.exit()

  if not os.path.exists(opt.fileName):
    print 'Error: Cannot file ',opt.fileName

  tgtLine = None
  for line in fileinput.input(opt.fileName):
    if lineNo is None:
      if keyWord in line:
        tgtLine = line
        break
    else:
      if fileinput.lineno() == lineNo:
        tgtLine = line
        break
  if tgtLine is None:
    if lineNo is None:
      print 'Error: cannot find line with keyword %s',keyWord
    else:
      print 'Error: cannot find line with line # %d',lineNo
  else:
    if sptr is None:
      cols = line.split()
    else:
      cols = line.split(sptr)
    print 'No. of cols = ',len(cols)
    for icol,col in enumerate(cols):
      print icol,col
      
         
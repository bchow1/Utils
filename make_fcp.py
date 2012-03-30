#
import sys
import re
import fileinput

srcPatt = re.compile(".*:\$\(BD\)(.*\.f90)\s+.*")

def writeSrcName(fOut,makeFile):
  for line in fileinput.input(makeFile+'.mak'):
    matchKey = srcPatt.match(line)
    if matchKey:
        matchString = matchKey.group(1).replace('/','\\')
        fOut.write('[fortran source file - ..\src%s]\n'%matchString)
        fOut.write('FileName=..\src%s\n'%matchString)
        fOut.write('IncludedForAnalysis=1\n\n')

def writeHead(fOut):

  fOut.write('[Main]\n')
  fOut.write('ident=FORCHECK project file\n')
  fOut.write('version=13.0\n')
  fOut.write('release=02\n')
  fOut.write('make_file=\n')
  fOut.write('Title=\n')
  fOut.write('Comments=\n')
  fOut.write('LastUsed_PW=132\n')
  fOut.write('LastUsed_PL=65\n')
  fOut.write('\n')
  fOut.write('[Project Options]\n')
  fOut.write('AC=0\n')
  fOut.write('CN=100\n')
  fOut.write('DC=0\n')
  fOut.write('DE=0\n')
  fOut.write('EX=0\n')
  fOut.write('F77=0\n')
  fOut.write('F90=0\n')
  fOut.write('F95=0\n')
  fOut.write('FF=1\n')
  fOut.write('OB=0\n')
  fOut.write('RE=0\n')
  fOut.write('INTR=0\n')
  fOut.write('DP=0\n')
  fOut.write('I2=0\n')
  fOut.write('I4=1\n')
  fOut.write('I8=0\n')
  fOut.write('SB=1\n')
  fOut.write('SS=1\n')
  fOut.write('SH=1\n')
  fOut.write('SI=1\n')
  fOut.write('SR=\n')
  fOut.write('SP=1\n')
  fOut.write('SC=\n')
  fOut.write('SM=\n')
  fOut.write('PW=132\n')
  fOut.write('PL=65\n')
  fOut.write('AP=1\n')
  fOut.write('CO=1\n')
  fOut.write('AR=1\n')
  fOut.write('RI=0\n')
  fOut.write('TR=0\n')
  fOut.write('INF=1\n')
  fOut.write('WA=1\n')
  fOut.write('LG=0\n')
  fOut.write(r'IP=..\src\scipuff\inc;..\src\aqueous\inc'+'\n')
  fOut.write('DF=\n')
  fOut.write('CR=1\n')
  fOut.write('UP=0\n')
  fOut.write('IL=\n')
  fOut.write('\n')

  return

if __name__ == '__main__':

  makeList = ['libaqaer','libarap','libsag','liblanduse','libmessages','libhpactool','libodepack','libfdatums','libscipuff','libswim','hpacstub'] 

  fOut = open('scipuff.fcp','w')
  writeHead(fOut)
  for makeFile in makeList:
    writeSrcName(fOut,makeFile)
  fOut.close()
  

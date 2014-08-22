import os
import sys
import fileinput
import difflib
  
os.chdir('D:\\SCIPUFF\\runs\\AFTAC\\omp\\p2')

diffOut = open('diff.out','w')

for line in fileinput.input('../repo/fort.77'):
  iPuff,iPass = map(int,line.strip().split())
  diffOut.write('%d, %d\n'%(iPuff,iPass))
  fName = '%06d.%03d'%(iPuff,iPass)
  repoFile = '../repo/' + fName
  lompFile = fName
  if os.path.exists(fName):
    diff=difflib.ndiff(open(repoFile).readlines(), open(lompFile).readlines())
    try:
      while 1:
        diffOut.write(diff.next())
    except:
      pass    
sys.exit()
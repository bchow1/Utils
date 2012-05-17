#
import os
import sys
#

def cmpCol(file1,file2):
  
  f1 = open(file1,'r')
  f2 = open(file2,'r')

  puffCSV = False
  isDiff  = False
  lineNo  = 0
  
  for line1,line2 in zip(f1,f2):

    lineNo += 1
    
    list1 = line1.strip().split(',')
    list2 = line2.strip().split(',')
    
    if lineNo == 1:
      if "Title" in list1[0]:
        puffCSV = True
        
    if puffCSV:
      if lineNo < 3:
        continue
      elif lineNo == 3:
        colHead1 = list1[:-1]
        colHead2 = list2[:-1]
        print colHead1[0],colHead1[-1]
        continue
      elif lineNo == 4:
        print lineNo,list1[:3]
    elif lineNo == 1:
      print lineNo,list1[:3]
    
    nlist1 = map(float,list1[:-1])
    nlist2 = map(float,list2[:-1])

    print 'time = ',nlist1[1],nlist2[1],lineNo
    for n1,n2 in zip(nlist1,nlist2):
      if abs(n1-n2) > 1e-16:
        print 'Found diff: ',n1,n2
        indx1 = nlist1.index(n1)
        indx2 = nlist2.index(n2)
        if puffCSV:
          print indx1,colHead1[indx1],colHead2[indx2]
        else:
          print indx1,indx2
        print 
        isDiff = True
        break
    if isDiff:
      if puffCSV:
        for colNo in range(len(nlist1)):
          print colHead1[colNo],nlist1[colNo],nlist2[colNo]
      else:
        print nlist1
        print nlist2        
      maxLine = lineNo
      break

  f1.close()
  f2.close()

  f1 = open(file1,'r')
  f2 = open(file2,'r')
  
  lineNo = 0
  for line1,line2 in zip(f1,f2):
    lineNo += 1
    if puffCSV and lineNo < 4:
      continue
    list1 = line1.strip().split(',')
    list2 = line2.strip().split(',')
    nlist1 = map(float,list1[:-1])
    nlist2 = map(float,list2[:-1])
    print nlist1[1],nlist1[indx1],nlist2[indx2]
    if lineNo == maxLine:
      break
  f1.close()
  f2.close()

  return

if __name__ == '__main__':

  file1 = 'x1.csv'
  file2 = 'x4.csv'
    
  if sys.platform == 'win32':
    runDir = "D:\hpac\\gitEPRI\\runs\\stepAmbwFlx"

  os.chdir(runDir)
  cmpCol(file1,file2)
    


  
  
  

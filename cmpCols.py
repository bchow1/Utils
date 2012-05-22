#
import os
import sys
#

def cmpCol(file1,file2):
  
  f1 = open(file1,'r')
  f2 = open(file2,'r')

  puffCSV  = False
  isDiff   = False
  absTol   = 1.  # 1e-16
  relTol   = 0.01
  lineNo   = 0
  maxLine  = 0
  diffCols = []
  maxCols  = 6
  maxLines = 5
  
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
        print 'Columns = ',colHead1[0],'...',colHead1[-1]
        continue
      elif lineNo == 4:
        print lineNo,list1[:3]
    elif lineNo == 1:
      print lineNo,list1[:3]
    
    nlist1 = map(float,list1[:-1])
    nlist2 = map(float,list2[:-1])

    print '\nReading: Time, ipuf, LineNo = ',nlist1[1],nlist1[0],lineNo
    for n1,n2 in zip(nlist1,nlist2):
      denom = max(1.e-30,abs(n1+n2))
      if abs(n1-n2) > absTol or abs(n2-n1)/denom > relTol:
        indx1 = nlist1.index(n1)
        indx2 = nlist2.index(n2)
        if indx1 not in diffCols:
          diffCols.append(indx1)
          if len(diffCols) > maxCols:
            break          
        if puffCSV:
          print '  %4d %12s %13.4e %13.4e %13.4e %13.4e'%\
                (indx1,colHead1[indx1],n1,n2,abs(n1-n2),abs(n2-n1)/denom)
        else:
          print indx1,indx2
        isDiff = True
    if isDiff:
      if puffCSV:
        if False:
          for colNo in range(0,len(nlist1),maxCol):
            colEnd = min(len(nlist1),colNo+maxCol)
            for i in range(colNo,colEnd):
              sys.stdout.write('%13s'%colHead1[i])
            sys.stdout.write('\n')
            for i in range(colNo,colEnd):
              sys.stdout.write('%13.4e'%nlist1[i])
            sys.stdout.write('\n')            
            for i in range(colNo,colEnd):
              sys.stdout.write('%13.4e'%nlist2[i])
            sys.stdout.write('\n\n')            
      else:
        print nlist1
        print nlist2        
      maxLine = lineNo
      if len(diffCols) > maxCols or maxLine > maxLines:
        break

  f1.close()
  f2.close()

  if maxLine > 0:
    
    f1 = open(file1,'r')
    f2 = open(file2,'r')
    if puffCSV:
      sys.stdout.write('\n\n')
      # Add time and ipuf to diffCols
      diffCols.insert(0,1)
      diffCols.insert(0,0)
      for colNo in diffCols:
        sys.stdout.write('%13s'%colHead1[colNo])
      sys.stdout.write('\n')
    lineNo = 0
    for line1,line2 in zip(f1,f2):
      lineNo += 1
      if puffCSV and lineNo < 4:
        continue
      list1 = line1.strip().split(',')
      list2 = line2.strip().split(',')
      if puffCSV:
        nlist1 = map(float,list1[:-1])
        nlist2 = map(float,list2[:-1])
        for colNo in diffCols:
          sys.stdout.write('%13.4e'%nlist1[colNo])
        sys.stdout.write('\n')
        for colNo in diffCols:
          sys.stdout.write('%13.4e'%nlist2[colNo])
        sys.stdout.write('\n\n')        
      else:
        nlist1 = map(float,list1[:-1])
        nlist2 = map(float,list2[:-1])
        print nlist1[1],nlist1[indx1],nlist2[indx2]
      if lineNo == maxLine:
        break
    f1.close()
    f2.close()

  return

if __name__ == '__main__':
    
  if sys.platform == 'win32':
    #runDir = "D:\hpac\\gitEPRI\\runs\\stepAmbwFlx"
    runDir = "J:\BNC\EPRI\\runs\\stepAmbwFlx"

  os.chdir(runDir)

  f1 = 'x1.csv'
  for f2 in ['x2.csv','x4.csv','x8.csv']:
    print '\nComparing ',f1,' and ',f2
    cmpCol(f1,f2)

  
  
  

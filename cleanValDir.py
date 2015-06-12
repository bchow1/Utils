import os 
import sys

Yr = 14
fList = os.listdir('./')
yList = []
for f in fList:
  if os.path.isdir(f):
    #print f,f[2:4]
    if f.startswith('14'):
      print f
      yList.append(f)
yList.sort()
#print yList

print
rList = open('RemoveDirList.tmp','w') 
for m in range(1,13):
  mList = []
  for y in yList:
    if y[2:4] == '%02d'%m:
      mList.append(y)
  print 'Month, No. of Directories = ',m,len(mList)

  xList = [mList[i] for i in range(0,len(mList),7)]
  print 'Excluding files : ',len(xList),xList
  
  for f in mList:
    if f not in xList:
      rList.write('%s '%f)
      print f
  print
rList.close()

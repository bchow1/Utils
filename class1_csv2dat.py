import pandas as pd

recep = pd.read_csv('SE_Class1.csv',names=['name','group','lat','long'],skiprows=4,usecols=(0,4,6,7))

print recep['name'][0]

print recep.head()
print recep.tail()

recDict = {
    'Cohutta':'cohu-recep.dat',
    'Great':'grsm2-recep.dat',
    'Joyce':'joyc-recep.dat',
    'Mammoth':'mamo2-recep.dat',
    'Shining':'shro-recep.dat'
     }
print recDict

fName = None
for irec in range(len(recep)):
  key = recep['name'][irec].split()[0]
  oName = recDict[key]
  print irec,oName
  if fName is not oName:
    if fName is not None:
      outFile.close()
      print 'Close',fName
    fName = oName
    print 'Open',fName
    outFile = open(fName,'w')
  outFile.write('%g %g %g\n'%(recep['long'][irec],recep['lat'][irec],recep['group'][irec]))
outFile.close()

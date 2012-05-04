#
import fileinput
import re
import os

os.chdir('D:\\hpac\\gitEPRI\\runs\\tva')

pufvars = 'xbar,ybar,zbar,det,c,cc,ccb,csav,sr,szz,vol,pres,temp,vself, \
           ityp,idtl,naux'
metvars = 'tb,pb,hb,cw,cc,prate,prbl,zinv,hp,us2,ws2,xml,zb1,zruf'
spcvars = 'taudry,tauwet,conc,amb'

'''
fOut = open('temp','w')
pct  = '%'

for vName in pufvars.split(','):
  v = vName.strip()
  print 'StepMCdat(isp)%spuff%s%s = p%s%s'%(pct,pct,v,pct,v)
  fOut.write('StepMCdat(isp)%spuff%s%s = p%s%s\n'%(pct,pct,v,pct,v))
fOut.write('\n')

for vName in metvars.split(','):
  v = vName.strip()
  print 'StepMCdat(isp)%spmet%s%s = %s'%(pct,pct,v,v)
  fOut.write('StepMCdat(isp)%spmet%s%s = %s\n'%(pct,pct,v,v))  
fOut.write('\n')

for vName in spcvars.split(','):
  v = vName.strip()
  print 'StepMCdat(isp)%schemSpc%s%s = chem%s%s'%(pct,pct,v,pct,v)
  fOut.write('StepMCdat(isp)%schemSpc%s%s = chem%s%s\n'%(pct,pct,v,pct,v))  
fOut.write('\n')

fOut.close()
'''

lftA = []
rgtA = []
nSpace = 0
for line in fileinput.input('temp1'):
  #print line
  if len(line.strip()) < 1:
    continue
  (lft,rgt) = line.strip().split('=')
  lftA.append(lft)
  rgtA.append(rgt)
  nSpace = max(nSpace,len(rgt)+1)
print nSpace

for i in range(len(lftA)):
  blank = ''
  for j in range(nSpace -len(rgtA[i])): 
    blank +=' '
  print '%s%s= %s'%(rgtA[i],blank,lftA[i])




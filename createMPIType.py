#
import fileinput
import re

pufvars = 'xbar,ybar,zbar,det,c,cc,ccb,csav,sr,szz,vol,pres,temp,vself, \
           ityp,idtl,naux'
metvars = 'tb,pb,hb,cw,cc,prate,prbl,zinv,hp,us2,ws2,xml,zb1,zruf'
spcvars = 'taudry,tauwet,conc,amb'

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

lftA = []
rgtA = []
nblank = 0
for line in fileinput.input('temp'):
  #print line
  if len(line.strip()) < 1:
    continue
  (lft,rgt) = line.strip().split('=')
  lftA.append(lft)
  rgtA.append(rgt)
  nblank = max(nblank,len(rgt))

blank = ''
for i in range(nblank): 
  blank +=' '

for i in range(len(lftA)):
  print '%s%s=%s'%(rgtA[i],blank,lftA[i])




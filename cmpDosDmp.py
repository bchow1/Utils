# -*- coding: utf-8 -*-
# <nbformat>2</nbformat>

# <codecell>

import pandas as pd

# <codecell>

def getDosTime(dosFile,verbose=False):
  df = pd.read_table(dosFile,sep='\s*',header=None)
  if verbose:
      print df.head(),'\n'
  dftime = df.loc[df.ix[:,0].str.contains('cell')]
  if verbose:
      print dftime.head(),'\n'
  df.columns = list(dftime.iloc[0])
  rowidx = list(dftime.index)
  rowidx.append(len(df))
  if verbose:
      print rowidx,'\n'
  dosByTime = []
  for tidx,row in enumerate(dftime.index):
    if verbose:
        print row+1,rowidx[tidx+1]-1
    dosByTime.append(df.iloc[row+1:rowidx[tidx+1]])
    if verbose:
        print dosByTime[-1].head(),'\n'
  if not verbose:
      print dosByTime[0].head(),'\n'
      print dosByTime[-1].head(),'\n'
  return dosByTime

# <codecell>

ser21_dos = getDosTime('3dclimo_ser_140421.txt')

# <codecell>

par21_dos = getDosTime('3dclimo_par_170421.txt')

# <codecell>

par14_dos = getDosTime('3dclimo_par_170414.txt')

# <codecell>

n1 = len(ser21_dos)
n2 = len(par14_dos)
print n1,n2
if not ( n1 == n2 ): 
    raise AssertionError,'Number of time breaks do not match: %d, %d'%(n1,n2)

# <codecell>

print ser21_dos[1]['cell'].iloc[[-1]].values[0]
print ser21_dos[1].tail()
print par14_dos[1]['cell'].iloc[[-1]].values[0]
print par14_dos[1].tail()

# <codecell>

for tidx in range(n1):
    cn1 = ser21_dos[tidx]['cell'].iloc[[-1]].values[0]
    cn2 = par14_dos[tidx]['cell'].iloc[[-1]].values[0]
    print tidx,cn1,cn2
    if not ( cn1 == cn2 ):
        raise AssertionError,'Number of cells %d and %d  at time break %d do not match'%(cn1,cn2,tidx)

# <codecell>

import numpy as np
for tidx in range(n1):
    diff_loc = np.where(ser21_dos[tidx] != par14_dos[tidx])
    df_from = ser21_dos[tidx].values[diff_loc]
    df_to   = par14_dos[tidx].values[diff_loc]
    print pd.DataFrame({'from':df_from,'to':df_to})
    print np.isclose(ser21_dos[tidx],par14_dos[tidx])
    np.cl

# <codecell>

print np.__version__


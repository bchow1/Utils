#!/bin/python
import os
import re

fList = os.listdir('./')
#endPatt = re.compile(r'(.*)_(\w{3})$')
endPatt = re.compile(r'(.*)_(ados)$')

for f in fList:
  matchKey = endPatt.match(f)
  if matchKey:
    if f.endswith('.bmp'):
      continue
    fnew = matchKey.group(1) + '.' +  matchKey.group(2)
    print f,' -> ',fnew
    os.renames(f,fnew)
  #else:
    #print f


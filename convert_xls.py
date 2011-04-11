#!/bin/env python
import os, sys
import re, fileinput

#fname=raw_input('Name of file to convert ?')
fname = 'try.txt'
sNo   = 5
pattEqual = re.compile(r"^\s*(.+)\t(.+)")

for line in fileinput.input( fname ):
  line = re.sub("\r\n","",line)
  if pattEqual.match(line):
    (col1,col2) = (pattEqual.match(line).group(1),pattEqual.match(line).group(2))
    col1 = re.sub("\t","        ",col1)
    col2 = re.sub("\t","        ",col2)
    col2 = re.sub("=","",col2)
    print 'B%d=%s !%s' %(fileinput.lineno()+sNo,col2.ljust(72),col1)
  else:
    line = re.sub("\t","        ",line)
    print '!B%d %s' %(fileinput.lineno()+sNo,line)

fileinput.close()

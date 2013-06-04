#!/bin/python
import sys

srcs=[]
for i in range(1, sys.argv.__len__()):
  srcs.append(sys.argv[i])
print "Src file %s\n"%srcs

colList = [[] for i in range(len(srcs))]
for isrc,fsrc in enumerate(srcs):
  inFile = open(fsrc,'r')
  for line in inFile:
    cols = line.strip().split()
    colList[isrc].append(cols)
  inFile.close()
for colno in range(len(colList[0][0])):
  for isrc,fsrc in enumerate(srcs):
    rowList = [] 
    rowList.append("%d"%colno)
    for col in colList[isrc]:
      rowList.append(" %s"%col[colno])
    print rowList

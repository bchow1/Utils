#!/usr/bin/env python
nThreads = raw_input("\nNumber of processors in order: ")
nThreads = nThreads.split()
RunTimes = raw_input("\nRun times in order: ")
RunTimes = RunTimes.split()
print 'Speeds up for :'
print 'Nproc    Time     SpeedUp'
rt0 = float(RunTimes[0])
for i in range(len(RunTimes)):
  nt = int(nThreads[i])
  rt = float(RunTimes[i])
  print '%2d %8.2f   %5.3f '% (nt,rt,rt0/rt)


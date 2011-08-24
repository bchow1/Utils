#!/home/user/bnc/local/bin/python
import os
import sys
import time
import fileinput

class Task():
  def __init__(self):
    self.name = ''
    self.estP = 0.
    self.actP = 0.
    self.totalT = 0.0
  def add(self,name,estP):
     self.name = name
     self.estP = estP

class Tasks():
   def __init__(self):
     self.taskList = []
   def add(self,name,estP,verbose=False):
     myTask = Task()
     myTask.add(name,float(estP))
     self.taskList.append(myTask)
     if verbose:
       tno = len(self.taskList)-1
       print 'Added task %d: %s, %g'%(tno,self.taskList[tno].name,self.taskList[tno].estP)
   def rm(self):
     for tno in range(len(self.taskList)-1,0,-1):
       task = self.taskList[tno]
       ans = raw_input('Remove task number %d: %s (y/n)? '%(tno,task.name))
       if len(ans) > 0 and ans[0].lower() == 'y': 
         print 'Removing task ',task.name          
         self.taskList.remove(task)
   def new(self):
     print '\nCurrent tasks:' 
     for tno in range(1,len(self.taskList)):
       task = self.taskList[tno]
       print '  ',tno,task.name,task.estP
     while True:
       ans = raw_input('Enter new task name and estimated P (enter to quit): ')
       if len(ans.strip().split()) == 2:
         name,estP = ans.strip().split()
         estP = float(estP)
         self.add(name,estP,verbose=True)
       else:
         break
   def update(self,taskNo,tadd,twork):
     self.taskList[taskNo].totalT += tadd
     self.taskList[taskNo].actP += tadd/twork
   def show(self,startNo=0):
     print '\n==========================='
     print 'No.  Name  EstP  ActP Ttime'
     print '==========================='
     for tno in range(startNo,len(self.taskList)):
       print tno,self.taskList[tno].name,self.taskList[tno].estP,self.taskList[tno].actP,self.taskList[tno].totalT
     print '==========================='
       
display = lambda x: sys.stdout.write(str(x)+"\n")

def show(msg):
  sys.stdout.write(msg + " ")
  sys.stdout.flush()

WORK_TICK  = "/usr/share/sounds/gnome/default/alerts/drip.ogg"
REST_TICK  = "/usr/share/sounds/gnome/default/alerts/drip.ogg"
ALARM      = "/usr/share/sounds/gnome/default/alerts/drip.ogg"
DEV_NULL   = open("/dev/null","w")

def tick(msg, duration, myTasks, tNo):
  "Print remaining mins for the duration given"
  global tStep
  nSteps = int(duration/tStep)
  display(msg + '  %d'%(nSteps*tStep))
  for iStep in range(nSteps):
    time.sleep(tStep*60)
    if iStep == 0:
      show('     %d'%(tStep*(nSteps-iStep-1)))
    else:
      show(' %d'%(tStep*(nSteps-iStep-1)))
    myTasks.update(tNo,tStep,duration)
  return

def alarm(msg, alarm):
  "Plays the alarm sound specified by alarm"
  #cmd = ["mpg123", alarm]
  #p = subprocess.Popen(cmd, stdout = DEV_NULL, stderr = subprocess.PIPE)
  #p.wait()
  display(" ")
  return

def doMore(myTasks):
  myTasks.show()
  doMore = raw_input('\nContinue(y)? ')
  ans = doMore.strip().upper()[0] 
  if ans == 'Y':
    return True
  return False

def readList(inputFile):
  completeList = []
  for line in fileinput.input(inputFile):
    if not line.startswith('#'):
      (name,estP) = line.strip().split(',')
      completeList.append([name,estP])
  for tno,task in enumerate(completeList):
    print tno,task[tno][0]
  tincl = rawinput('Enter taskNos to include').split()
  myTasks = Tasks()
  myTasks.add('Mauj',0)
  for tno,task in enumerate(completeList):
    if tno in tincl: 
      myTasks.add(name,estP,verbose=True)
  return(myTasks)

def saveList(inputFile,myTasks):
  fTask = open(inputFile,"a",0)
  for tno in range(1,len(myTasks.taskList)):
    fTask.write('%d, %s, %g\n'%(tno,myTasks.taskList[tno].name,myTasks.taskList[tno].estP))
  fTask.close()

def chngList(inputFile,myTasks):
  myTasks.rm()
  myTasks.new()
  return(myTasks)

def runPomo(myTasks,twork,trest):

  global nTimes

  while True:
    try:
      print  '\nAvailable tasks:'
      myTasks.show(startNo=1)
      while True:
        taskNo = int(raw_input('No.? '))
        if taskNo <= len(myTasks.taskList):
          break
      curTask = myTasks.taskList[taskNo]
      for tm in range(nTimes):
        (tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec,tm_wday,tm_yday,tm_isdst) = time.localtime()
        if taskNo > 0:
          msg = " %s (%02d:%02d) "%(curTask.name, tm_hour,tm_min)
          tick('(%02d)'%(int(curTask.actP)+1) + msg, twork,  myTasks, taskNo)
          alarm(msg, ALARM)
        if tm == nTimes-1:
          msg = '     Aish'
          tick('(%02d)'%(int(curTask.actP)+1) + msg,  trest*2,  myTasks, taskNo)
          alarm(msg, ALARM)
          if not doMore(myTasks): return 0
        else:
          msg = '     Mauj'
          tick('(%02d)'%(int(curTask.actP)+1) + msg,  trest,  myTasks, taskNo)
          alarm(msg, ALARM)
    except KeyboardInterrupt:
      if not doMore(myTasks): return 0

if __name__ == "__main__":

  global tStep
  global nTimes

  args = sys.argv
  print "\nUsage : %s work_time rest_time [ntimes]\n"%sys.argv[0]
  
  if len(args[1:]) < 2:
    twork = 25.
    trest = 5.
    print 'Using default values of 30., 5., and 2'
  else:
    twork, trest = map(float,args[1:3])
    if len(args[1:]) == 3:
      nTimes = int(args[3])

  # No. of pomos for big break
  nTimes = 2

  # Display times in mins
  tStep = 2
 
  #
  inputFile = '/home/user/bnc/notes/trackPomo/tasklist.tpi'
  print 'Reading tasks from ',inputFile
  myTasks = readList(inputFile)
  #
  editList = raw_input('\nChange task list (y/n)? ')
  if editList[0].lower() == 'y':
    myTasks = chngList(inputFile,myTasks)
    saveList(inputFile,myTasks)
  #
  #runPomo(myTasks,twork,trest)

#!/usr/bin/env python
"""
Emulates a pomodoro timer.

The program is invoked with a "work duration" and a "rest duration".
It plays a ticking sound for the work duration (specified in minutes) and then an alarm.
After that it plays another tick for the rest duration (also specified in minutes).

If the PyOSD library is available, it will use it to display messages
on the screen. Otherwise, it simply prints them out to stdout.

This is usually invoked as
./ticker.py 30 5
This means that you work for 30 minutes and then rest for 5.

For details on the Pomodoro technique, please refer http://www.pomodorotechnique.com/
For the sound files, please check out http://www.soundjay.com/clock-sounds-1.html

This script is an attempt to create an offline version of http://www.focusboosterapp.com/live.cfm

"""

import sys
import time
import subprocess

pyosd = False
try:
    import pyosd
    osd = pyosd.osd()
    osd.set_align(pyosd.ALIGN_CENTER)
    osd.set_pos(pyosd.POS_MID)
    display = osd.display
    show = osd.display
except:
    display = lambda x: sys.stdout.write(str(x)+"\n")
    def show(msg):
      sys.stdout.write(msg + " ")
      sys.stdout.flush()
    
#WORK_TICK = "/home/noufal/scratch/clock-ticking-4.mp3"
#REST_TICK = "/home/noufal/scratch/clock-ticking-5.mp3"
#ALARM     = "/home/noufal/scratch/alarm-clock-1.mp3"
WORK_TICK  = "/usr/share/sounds/gnome/default/alerts/drip.ogg"
REST_TICK  = "/usr/share/sounds/gnome/default/alerts/drip.ogg"
ALARM      = "/usr/share/sounds/gnome/default/alerts/drip.ogg"
DEV_NULL   = open("/dev/null","w")

def tick(msg, duration, tick):
    "Plays a the ticking sound specified by tick for duration time"
    #cmd = ["mpg123", "--loop", "-1" , tick]
    #p = subprocess.Popen(cmd, stdout = DEV_NULL, stderr = subprocess.PIPE)
    tStep = 2
    n4 = int(duration/tStep)
    display(msg + ' karo %d'%(n4*tStep))
    for m5 in range(n4):
      time.sleep(tStep*60)
      #time.sleep(tStep)
      if m5 == 0:
        show('     %d'%(tStep*(n4-m5-1)))
      else:
        show(' %d'%(tStep*(n4-m5-1)))
    #p.kill()
    
def alarm(msg, alarm):
    "Plays the alarm sound specified by alarm"
    #cmd = ["mpg123", alarm]
    #p = subprocess.Popen(cmd, stdout = DEV_NULL, stderr = subprocess.PIPE)
    #p.wait()
    display(" ")

def doMore():
  doMore = raw_input('\nContinue(y)? ')
  ans = doMore.strip().upper()[0] 
  if ans == 'Y':
    return True
  return False
  
    
def main(args):
    if len(args[1:]) < 2:
      print "Usage : %s work_time rest_time"%args[0]
      return -1
    twork, trest = map(float,args[1:3])
    totwrk = 0
    totrst = 0
    if len(args[1:]) == 3:
      m20t = int(args[3])
    else:
      m20t = 4
    while True:
      try: 
        for m20 in range(m20t): 
          msg = " Kaam"
          tick('(%02d)'%(m20+1) + msg, twork, WORK_TICK)
          totwrk += twork
          alarm(msg, ALARM)
          if m20 == m20t-1:
            msg = '     Aish'
            tick(msg, trest*2, REST_TICK)
            totrst += trest*2
            alarm(msg, ALARM)
            display("\nKaam %d, Aish %d"%(totwrk,totrst))
            if not doMore(): return 0
          else:
            msg = '     Mauj'
            tick(msg, trest, REST_TICK)
            totrst += trest
            alarm(msg, ALARM)
      except KeyboardInterrupt:
        if not doMore(): return 0
    #display("")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

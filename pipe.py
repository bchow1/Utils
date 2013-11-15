#!/usr/bin/env python
# pipe.py
try :
  from queue import Queue ,Empty 
except ImportError :# <strong class="highlight">python</strong> < 3.0
  from Queue import Queue ,Empty 
from threading import Thread 

class TimeoutError (Exception ):
  pass 

class Pipe (object ):
  """A wrapper around a pipe opened for reading"""
  def __init__ (o ,pipe ):
    o .pipe =pipe 
    o .queue =Queue ()
    o .thread =Thread (target =o ._loop )
    o .thread .start ()
  def readline (o ,timeout =None ):
    "A non blocking readline function with a timeout"
    try :
      return o .queue .get (True ,timeout )
    except Empty :
      raise TimeoutError 
  def _loop (o ):
    try :
      while True :
        line =o .pipe .readline ()
        o .queue .put (line )
    except (ValueError ,IOError ):# pipe was closed
      pass 
  def close (o ):
    o .pipe .close ()
    o .thread .join ()

def testme ():
  """Start a subprocess and read its stdout in a non blocking way""" 
  import subprocess 
  prog ="pipetest.py"
  child =subprocess .Popen (
  "python %s"%prog ,
  shell =True ,
  stdout =subprocess .PIPE ,
  close_fds =True ,
  )
  pipe =Pipe (child .stdout )
  for i in range (20 ):
    try :
      line =pipe .readline (1.45 )
      print ("[%d] %s"%(i ,line [:-1 ]))
    except TimeoutError :
      print ("[%d] readline timed out"%i )
  pipe .close ()
  print("pipe was closed")

if __name__ =="__main__":
  testme ()

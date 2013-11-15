#!/usr/bin/env python
# pipetest.py
from itertools import count 
from time import sleep 
import sys 

try :
  for i in count (0 ):
    print ("line %d"%i )
    sys .stdout .flush ()
    sleep (3 )
except IOError :# stdout was closed
  pass

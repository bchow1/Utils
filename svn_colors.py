#!/usr/bin/python
"""
 Author: Saophalkun Ponlu (http://phalkunz.com)
 Contact: phalkunz@gmail.com
 Date: May 23, 2009
"""

import sys, os, re

# add more status & color codes
colors = {
    "M": "31",      # red
    "\?": "32",     # green
    "C": "30;41"    # black on red
}

# build a paramter list
parameters = "";
for i in range(1, sys.argv.__len__()):
    parameters += sys.argv[i] + " ";

status = os.popen('svn st ' + parameters);
for line in status:
    passed = False
    # remove newline character from the line
    line = re.sub("\n", "", line)
   
    for color in colors:
        match = re.match(color+(" "*6), line)
        if match:  
            os.popen("echo '\E[" + colors[color] + "m" + line + "\E[m'", 'w')
            passed = True
    if(passed):
        continue
       
    os.popen("echo \"" + line + "\"", 'w')

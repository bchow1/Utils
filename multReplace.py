#!/bin/python

# Program to replace HPAC with SCIP or viceversa in a file or directory

import os
import sys
import optparse
import re
import shutil

def multiple_replacer(reverse,*key_values):
  
    if reverse:
      replace_dict ={}
      for k,v in key_values:
        replace_dict.update({v:k})    
      pattern = re.compile("|".join([re.escape(v) for k,v in key_values]), re.M)
    else:
      pattern = re.compile("|".join([re.escape(k) for k,v in key_values]), re.M)
      replace_dict = dict(key_values)
    replacement_function = lambda match: replace_dict[match.group(0)]
    return lambda string: pattern.sub(replacement_function, string)

def multiple_replace(string,reverse,*key_values):
    return multiple_replacer(reverse,*key_values)(string)

# Parse arguments
arg = optparse.OptionParser()
arg.add_option("-n",action="store",type="choice",choices=["yes","no"],dest="dryrun")
arg.add_option("-i",action="store",type="string",dest="inName")
arg.add_option("-s",action="store",type="string",dest="keyword")

arg.set_defaults(dryrun="yes",keyword=None)
opt,args = arg.parse_args()

if opt.inName is None:
  print 'Error: keyword, suffix or prefix must be specified'
  print 'Usage: multReplace.py [-s hpac|scip ] [-i inName ] [ -n yes]'
  sys.exit()

inName = opt.inName

if opt.dryrun.lower() == 'no':
  lDry = False
else:
  lDry = True

if opt.keyword is not None:
  subStr  = opt.keyword
else:
  subStr = 'hpac'  

if subStr == 'scip':
  reverse = True 
else:
  reverse = False

'''  
  replacements = (u"sciptool", u"hpactool"),\
                 (u"SCIPGet",  u"HPACGet"),\
                 (u"SCIPtool", u"HPACtool"),\
                 (u"SCIPsuccess", u"HPACsuccess"),\
                 (u"SCIPNum",  u"HPACNum")
                 
elif subStr == 'hpac':
'''
    
replacements = (u"hpactool",    u"sciptool"),\
               (u"HPACInit",    u"SCIPInit"),\
               (u"HPACGet",     u"SCIPGet"),\
               (u"HPACtool",    u"SCIPtool"),\
               (u"HPACsuccess", u"SCIPsuccess"),\
               (u"HPACFailure", u"SCIPFailure"),\
               (u"HPACoff",     u"SCIPoff"),\
               (u"HPACNum",     u"SCIPNum"),\
               (u"HPACExit",    u"SCIPExit")
               
if os.path.isdir(inName):
  fList = os.listdir("./")
elif os.path.exists(inName):
  fList = [inName]
else:
  print 'Error: cannot find file or directory named %s'%inName
  sys.exit()
  
print replacements  
  
for inName in fList:
  
  if os.path.isdir(inName):
    continue
  inFile  = open(inName,'r')
  outName = inName + '.' + subStr
  outFile = open(outName,'w')
  
  for line in inFile:
    print '0:',line  
    newLine = multiple_replace(line,reverse,*replacements)
    print '1:',newLine
    outFile.write(newLine)
  
  inFile.close()
  outFile.close()
  
  if not lDry:
    print 'Renaming %s -> %s'%(outName,inName)
    shutil.move(outName,inName)
  else:
    print 'Dryrun: Renaming %s -> %s'%(outName,inName)

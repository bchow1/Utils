#

import os
import sys
import fileinput
import optparse
import pandas as pd

print os.getcwd()


# Call main program
if __name__ == '__main__':
  
  #os.chdir('d:\\SCIPUFF\\EPRI\\runs\\negativeO3\\SCICHEM-ROME')
  
  # Parse arguments
  arg = optparse.OptionParser()
  arg.add_option("-f",action="store",type="string",dest="fileName")
  arg.add_option("-n",action="store",type="string",dest="colNames")
  arg.add_option("-r",action="store",type="string",dest="skipRows")
  arg.add_option("-u",action="store",type="string",dest="useCols")
  arg.add_option("-s",action="store",type="string",dest="separator")
  arg.set_defaults(fileName=None,colNames=None,skipRows=None,useCols=None,separator=None)
  opt,args = arg.parse_args()

  if opt.fileName is None :
    print 'Error: File name must be specified'
    print 'Usage: getSum.py -f fileName [-n colName1,..,colNameN] [-r rows] [-u col1,..,colN] [-s separator]'
    sys.exit()

  #'out_fourCorners/o3.DV.max',names=['X','Y','Value'],delim_whitespace=True,skiprows=1,usecols=[1,2,3])

  if not os.path.exists(opt.fileName):
    print 'Error: Cannot file ',opt.fileName
    sys.exit()
  else:
    fileName = opt.fileName

  if fileName.endswith('.max') or fileName.endswith('.xyz'):
    isXYZ = True
  else:
    isXYZ = False

  if opt.colNames is None:
    if isXYZ:
      colNames = ['X','Y','Value']
    else:
      colNames = None
  else:
    colNames = opt.colNames.split(',')

  if opt.separator is None:
    delim_whitespace = True
    separator = None
  else:
    delim_whitespace = False 
    separator = opt.separator

  if opt.skipRows is None:
    if isXYZ:
      skipRows = 1
    else:
      skipRows = None
  else:
    skipRows = int(opt.skipRows)

  if opt.useCols is None:
    if isXYZ:
      useCols = [1,2,3]
    else:
      useCols = None
  else:
    useCols = opt.useCols.split(',')
 
  print '**'
  print fileName
  print colNames
  print delim_whitespace
  print separator
  print skipRows
  print useCols
  print '**'

  df  = pd.read_csv(fileName,names=colNames,delim_whitespace=delim_whitespace,sep=separator,skiprows=skipRows,usecols=useCols)
  print df.describe()


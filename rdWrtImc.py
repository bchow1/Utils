#
# Read section name from imc file
# and save the species data in spList
# 
import os
import sys
import sqlite3
import numpy as np

MAX_MC = 250

def rdSpSec(line,spList):
  spList.append(line.strip().split())
  return spList

def rdImc(imcName):
  imcFile  = open(imcName,'r')
  sctnName = None

  # Initialize spList
  spList   = []

  # Read section name and data from each line
  for line in imcFile:
    if len(line.strip()) > 0: 
      if line.startswith('#'):
        sctnName = line.strip().split()[0].replace('#','').split(',')[0]
        print 'Section = ',sctnName
        continue
      if sctnName == 'Species':
        rdSpSec(line,spList)
  imcFile.close()
  print len(spList),spList[0],spList[-1]
  return spList

def rdMCScn(scnName):
  
  scnFile = open(scnName,'r')
  scnList = []
  
  inScn = False
  for line in scnFile:
    lStrip = line.strip()
    if len(lStrip) > 0: 
      if lStrip.startswith('&SCN'):
        print 'Start Scn ',len(scnList)+1
        inScn = True
        scnLines = []
        relList  = []
      if lStrip.startswith('/'):
        scnList.append([scnLines,relList])
        inScn = False
        print 'End Scn ',len(scnList)
      # Reads SCICHEM-99 type MC release
      if inScn:
        if 'REL_MC' in line:
          if lStrip.endswith(','):
            lStrip = lStrip[:-1]
          relList = map(float,lStrip.split('=')[1].strip().split(','))
          print len(relList)
        else:
          scnLines.append(line)
  scnFile.close()

  return scnList

def wrtMCScn(spList,scnList,newRel=None,newSpList=None,fmt=None,spSkip=None):
  
  # This function writes a scn file. If newRel is present
  # then the MC release mass is taken from newRel
  # If fmt is New then the scn file is written with START_MC
   
  # Get names and ambient concentrations from new spList 
  if newRel is not None:
    spNames = [spVal[0] for spVal in spList]
    spConcs = [spVal[2] for spVal in spList]

  if newSpList is not None:
    newSpNames = [spVal[0] for spVal in newSpList]
    newSpConcs = [spVal[2] for spVal in newSpList]
        
  scnFile = open('temp.scn','w')
  for scnNo,scnVal in enumerate(scnList):
    print '\n#START_MC ',scnNo+1
    if fmt == 'New':
      rel_mc = []
      rel_mc.append('#START_MC\n')
    for line in scnVal[0]:
      scnFile.write('%s'%line)
    for spNo in range(len(spList)):
      if scnVal[1][spNo] != 0.:
        print '     ',spList[spNo][0],scnVal[1][spNo]
        if fmt == 'New' and newRel is None:
          if spSkip is not None:
            if spList[spNo][0] in spSkip:
              continue
          rel_mc.append('     %s %s\n'%(spList[spNo][0],scnVal[1][spNo]))
        
    if newRel is not None:
      print '#NEW_MC ',scnNo+1
    else:
      print '#END_MC ',scnNo+1
    
    # Replace relList with newRel values 
    if newRel is not None:
      for spNo in range(len(scnVal[1])):
        scnVal[1][spNo] = 0.
      for spName,spConc in newRel.iteritems():
        spIndx = spNames.index(spName) 
        scnVal[1][spIndx] = spConc
      for spNo in range(len(spList)):
        if scnVal[1][spNo] != 0.:
          print '     ',spList[spNo][0],scnVal[1][spNo]
          if fmt == 'New':
            if spSkip is not None:
              if spList[spNo][0] in spSkip:
                continue
            rel_mc.append('     %s %s\n'%(spList[spNo][0],scnVal[1][spNo]))
      print '#END_MC ',scnNo+1
    
    if fmt == 'New':
      scnFile.write('/\n')
      for relmc in rel_mc:
        scnFile.write(relmc)
      scnFile.write('#END_MC\n')
    else:           
      scnFile.write(' REL_MC = ')
      for spRel in scnVal[1]:
        scnFile.write('%13.5e,'%spRel)
      for i in range(len(scnVal[1]),MAX_MC):
        scnFile.write('%13.5e,'%0.)
      scnFile.write('\n/\n')
  return

def wrtImcSpList(spList,newSpList):
  # This function writes species section of an imc file using the 
  # background concentrations from newSpList
   
  # Get names and ambient concentrations from new spList 
  spNames = [spVal[0] for spVal in spList]
  spConcs = [spVal[2] for spVal in spList]

  newSpNames = [spVal[0] for spVal in newSpList]
  newSpConcs = [spVal[2] for spVal in newSpList]
  
  fmtList = ['10s','12s','18s','13s','9s','3s','6s']  
  sfmt = '' 
  for idx,fmt in enumerate(fmtList):
    sfmt = sfmt + '{0[%d]:%s} '%(idx,fmt)
  sfmt = sfmt + '\n'
  
  for spNo,spName in enumerate(spNames):
    try:
      indx = newSpNames.index(spName)
      if abs(float(spConcs[spNo]) - float(newSpConcs[indx])) > 1.e-10:
        spList[spNo][2] = newSpConcs[indx]
        print 'For %s replacing amb = %s with %s'%(spName,spConcs[spNo],newSpConcs[indx])
    except ValueError:
      print 'Note: Cannot find %s in new species list '%spName

  imcFile = open('temp.imc','w')
  imcFile.write('#Species,Type,Ambient,Tolerance,deposition vel,wet scav,mw\n')
  for line in spList:
    imcFile.write(sfmt.format(line))
  imcFile.close()   
  
  return                                                    
      
def openDb(dbName):
  dbConn = sqlite3.connect(dbName)
  dbConn.row_factory = sqlite3.Row
  dbCur  = dbConn.cursor()
  return (dbConn,dbCur)

def dbExecuteStmts(dbName):
  dbConn,dbCur = openDb(dbName)
  dbCur.execute('DROP table if exists concTable')
  dbCur.execute('CREATE table concTable ( speciesName varChar(8), speciesType varChar(2), ambConc real , tolerence real)')
  return (dbConn,dbCur)

def insertData(dbConn,dbCur,spList):
  for i in range(0, len(spList)-1):
    #print spList[i][0], spList[i][1], spList[i][2]
    insertStr = "INSERT into concTable VALUES('%s', '%s', %13.5e, %13.5e)"%(spList[i][0],spList[i][1],float(spList[i][2]),float(spList[i][3]))
    #print insertStr
    dbCur.execute(insertStr)
  dbConn.commit()
    
def createDB(spList):
  dbName = 'scichem99_amb_vals.db'
  dbConn,dbCur = dbExecuteStmts(dbName)  
  insertData(dbConn,dbCur,spList)
  
# Main Program

if __name__ == '__main__':
  
  # Get new species background from input imc file 
  if True:
    curDir = os.getcwd()
    #Input directory
    #
    
    #inpDir = 'D:\\SCIPUFF\\EPRI\\runs\\negativeO3'
    #imcName = 'scichem-2012\\negO3_1hr_fix.imc'
    
    #inpDir = 'd:\\SCIPUFF\\EPRIx\\SCICHEM-2012\\runs\\JAWMA_CMAS_2012\\tva\\tva_990706'
    #imcName = 'SCICHEM-ROME\\070699_vo3.imc'
    
    inpDir = 'V:\\TestSCICHEM\\Outputs\\130327.HiISOPF\\Chemistry\\tva_990706\\'
    imcName = 'FixEmis_CBL_ZMET_noLSV_hiVOC\\cumberland.imc'
    
    os.chdir(inpDir)
    newSpList = rdImc(imcName)
    os.chdir(curDir)
  
  # Get new release list
  newRel = {'NO2':3.21E+02,'NO':2.885E+03,'SO2':5.76E+02} 
  spSkip = ['HG0','HG2','SO4_1','HGP_1']
  
  # Output directory
  #
  
  #runDir = 'D:\\SCIPUFF\\EPRI\\runs\\negativeO3'
  #imcName = 'scichem-ROME\\negO3_1hr_fix.imc'
  #scnName = 'scichem-ROME\\negO3_1hr_fix.scn'
  #
  #runDir = 'd:\\SCIPUFF\\EPRIx\\SCICHEM-2012\\runs\\JAWMA_CMAS_2012\\tva\\tva_990706'
  
  #imcName = 'SCICHEM-2012\\ae5_rome.imc'
  #imcName = 'SCICHEM-99\\tva_990706_romebg.imc'

  #runDir = 'D:\\negativeO3\\' 
  
  runDir = 'V:\\TestSCICHEM\\Outputs\\130327.HiISOPF\\Chemistry\\tva_990706'
  imcName = 'FixEmis_CBL_ZMET_noLSV_hiVOC\\ae5_noamb.imc'
  scnName = 'SCICHEM-v2100\\test01_v2100.scn'
  
  os.chdir(runDir)
  spList = rdImc(imcName)
  #createDB(spList)
  #scnList = rdMCScn(scnName)
  
  #
  #wrtMCScn(spList,scnList,fmt='New',spSkip=spSkip)
  wrtImcSpList(spList,newSpList)
  


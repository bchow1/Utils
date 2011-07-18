#!/bin/env /bin/python
import re
import fileinput
import os
import sys
import shutil
import run_cmd


class Pattern(object) :

  def __init__(self):
 
    self.nmlinp     = ['ctrl','time1','time2','flags','domain','options','matdef']
    self.nmlmsc     = ['met']
    self.nmlscn     = ['scn']
    self.pattEndNml = re.compile(".*/.*")
    self.pattStaNml = re.compile('\s*&(\w+)\s*',re.I)
    self.pattNml = {}
    self.Nml     = {}
    for nml in self.nmlinp + self.nmlmsc + self.nmlscn:
      list = {}
      pattlist = {}
      # From inp file
      if nml == 'ctrl':
        list.update({'restart':"F",'file_rst':"''",'path_rst':"''",'time_rst':0.0})
      if nml == 'time1':
        list.update({'year_start':2000,'month_start':1,'day_start':1,'tstart':0.0})
        list.update({'tzone':16.0,'local':"F"})
      if nml == 'time2':
        list.update({'year_end':2000,'month_end':1,'day_end':1,'tend':0.5})
        list.update({'tend_hr':0.5,'delt':60.,'dt_save':60.})
      if nml == 'flags':
        list.update({'title':"''",'create':'T','audit_class':'Unclassified'})
        list.update({'audit_analyst':"''",'dynamic':"F",'dense_gas':"F",'static':'T'})
        list.update({'hazarea':"Off",'run_mode':0,'prjeffect':0})
      if nml == 'domain':
        list.update({'cmap':"'CARTESIAN'",'xmin':0.,'xmax':1.})
        list.update({'ymin':0.,'ymax':1.,'zmax':2500.})
        list.update({'vres':1.e36,'hres':1.e36,'utm_zone':12})
        list.update({'xref':0.,'yref':0.,'lon0':-112.994,'lat0':40.08413})
      if nml == 'options':
        list.update({'t_avg':1.e36,'cmin':1e-20,'lsplitz':"F",'delmin':1.e36})
        list.update({'wwtrop':0.01,'epstrop':4e-04,'sltrop':10.0,'uu_calm':0.25})
        list.update({'sl_calm':1000.0,'nzbl':11,'mgrd':2,'z_dosage':0.0e0})
        list.update({'smpfile':"''",'dt_smp':1.e36,'substrate_type':0})
      if nml == 'matdef':
        list.update({'class':"'gas'",'mname':"'tracer'",'units':"'kg'",'file_name':"''"})
        list.update({'file_path':"''",'group_deposition':"F",'group_dose':"F",'multi_comp':"F"})
        list.update({'conc_min':0.e0,'decay_amp':0.e0,'decay_min':0.e0})
        list.update({'density':1.2,'gas_deposition':0.e+0})
        list.update({'effectclass':0,'effectavail':0})
      # From scn file
      if nml == 'scn':
        list.update({'relname':"''",'reldisplay':"'<empty>'",'trel':0.0})
        list.update({'xrel':2.137133,'yrel':-5.5464860e-02,'zrel':1.0})
        list.update({'cmass':33.0,'subgroup':1,'sigx':0.10,'sigy':0.10})
        list.update({'sigz':0.10,'wmom':0.0,'buoy':0.0})
        list.update({'lognorm_mmd':-1.e36,'lognorm_sigma':-1.e36})
        list.update({'slurry_fraction':-1.e36,'number_random':-65535})
        list.update({'random_spread':-1.e36,'random_seed':-65535})
        list.update({'horiz_uncertainty':-1.e36,'vert_uncertainty':-1.e36})
        list.update({'relstatus':1,'reltyp':"'C'",'relmat':"'tracer'",'tdur':0.25})
      if nml == 'met':
        list.update({'met_type':"'obs'",'bl_type':"'oper'",'ensm_type':"'oper3.1'",'uu_ensm':0.0})
        list.update({'sl_ensm':100000.0,'zimin':50.0,'zimax':1000.000,'hconst':0.0})
        list.update({'hdiur':50.0,'h_cnp':-1.00,'alpha_cnp':0.000e+00,'zruf':1.000e-02})
        list.update({'sl_haz':100000.0,'albedo':0.3,'bowen':4.0,'cloud_cover':5.001e-02})
        list.update({'local_met':"F",'nearest_sfc':65535,'nearest_prf':65535,'lmc_ua':"F",'alpha_max':1.0})
        list.update({'alpha_min':1.0e-03,'max_iter_ac':200,'ac_eps':1.0e-02,'max_iter':100})
        list.update({'p_eps':1.0e-05,'nzb':23})
        list.update({'zb':'50.0,150.0,261.4300,385.4140,523.1650,675.9950,845.3170,1032.650,\
                      1239.620,1467.990,1719.600,1996.440,2300.620,2634.360,3000.000,3400.000,\
                      3892.620,4503.540,5266.700,6227.120,7444.830,9000.000,11000.00,177*0.0'})
        list.update({'file_ter':'','lout_mc':"F",'lout_met':"F",'tout_met':-1.e36})
        list.update({'lout_3d':"F",'lout_2d':"F",'pr_type':'NONE','tbin_met':60.00000e+00})
        list.update({'i_wet':2,'dt_swift':1.e36,'mctype':0,'lformat':"F"})
        list.update({'metfile':""})

      # build Nml and pattNml dictionary
      # Nml['ctrl'] = {restart:F} etc.
      # pattNml['ctrl'] = {restart:pattern_restart} etc.
      if len(list) > 0:
        self.Nml.update({nml:list})
        for vname in list.keys():
          #cPattern = str('(.*%s\s*=\s*)(.*?)(,.*)'%vname)
          cPattern = str('(.*%s\s*=\s*)(.*?)($)'%vname)
          #print vname, cPattern
          rPattern = re.compile(cPattern,re.I)
          if vname == 'metfile':
            rPattern = re.compile("(.*@)(\d{3}.+)(\s*.*)")
          if vname == 'smpfile':
            rPattern = re.compile("(.*%s\s*=\s*')(.*)('\s*,.*)"%vname,re.I)
          pattlist.update({vname:rPattern})
        self.pattNml.update({nml:pattlist})
      else:
        print 'Warning: cannot find list for ',nml

    # Combine all namelist variables ( does not check for duplicates)
    self.pattNameList = {}
    for nml in self.nmlinp + self.nmlmsc + self.nmlscn:
      for key in self.pattNml[nml].keys():
        self.pattNameList.update({key:self.pattNml[nml][key]})
    
    # project log files
    self.pattNterm  = re.compile("Normal termination")             # Normal termination 

    # sampler input and output files
    self.pattSmpT  = re.compile("(HPAC)|(SCIPUFF)\s*",re.I)        # Sampler type
    self.pattSmp1  = re.compile("(.+)001")                         # First sampler

    # ntv file keywords
    self.pattRelTime = re.compile("^Time(.+)\((.+?)\s+(.+)\s+\)")
    self.pattRelLoc  = re.compile("^Field max(.+):\s*(.+?)\s+(.+?)\s+(.+)")

    # sum file keywords
    self.pattMassEst = re.compile("^\s*Mass\s+Estimate(.+)")

  def addNml(self,line,mLine):
    line = re.sub("\s*&\w+\s*","",line)
    line = re.sub("/","",line)
    splitLine = line.split(',')
    if len(splitLine) == 2:
      mLine.append(splitLine[0])
    else:
      for i in splitLine:
        mLine.append(i)
    return(mLine)

  def chkNml(self,nmlFile):
    nmlName  = None 
    nmlLines = []
    isNml    = False
    for line in nmlFile:
      #print 'line = ',line
      line = re.sub("\n","",line)
      line = re.sub("\r","",line)
      line.strip()
      matchStaNml = self.pattStaNml.match(line)
      matchEndNml = self.pattEndNml.match(line)
      if matchStaNml:
        #print 'match start'
        mLine = []
        mLine = self.addNml(line,mLine)
        nmlName = matchStaNml.group(1).lower()
        # Namelist ending on same line
        if matchEndNml:
          #print 'match end'
          isNml = False
          nmlLines = mLine
          break
        else:
          isNml = True
      if isNml and matchEndNml:
        #print 'match end'
        mLine = self.addNml(line,mLine)
        isNml = False
        nmlLines = mLine
        break
      if isNml and not matchStaNml:
        mLine = self.addNml(line,mLine)
    return(nmlName,nmlLines)

  def readNml(self,inFile):

    nmlFile  = open(inFile,'r')
    nmlNames  = []
    nmlValues = []
    while True:   
      (nameList,nmlLines) = self.chkNml(nmlFile)
      if nameList: 
        nmlNames.append(nameList)
        nmlValue = self.Nml[nameList].copy()
        for line in nmlLines:
          for key in self.Nml[nameList]:
            matchNmlKey = self.pattNml[nameList][key].match(line)
            #matchNmlKey = self.pattNameList[key].match(line)
            if matchNmlKey:
              nmlValue.update({key:matchNmlKey.group(2)})
        nmlValues.append(nmlValue)
      else:
        nmlFile.close()
        break
    return(nmlNames,nmlValues)

class Files(object):

  def __init__(self,prjName,mySCIpattern):

    self.prjName = prjName
    #print prjName

    # input files
    self.inpFile = self.prjName + '.inp'
    self.mscFile = self.prjName + '.msc'
    self.scnFile = self.prjName + '.scn'
    self.inpList = dict([('inp',self.inpFile),('msc',self.mscFile),('scn',self.scnFile)])
      
    # output file
    self.prjFile = self.prjName + '.prj'
    self.logFile = self.prjName + '.log'
    self.pufFile = self.prjName + '.puf'
 
    # Read sam file from inpfile
    self.getSamFile(mySCIpattern)

  def getSamFile(self,mySCIpattern):
    self.samFile = None
    self.smpFile = self.prjName + '.smp'
    if not os.path.exists(self.inpFile):
      print 'Error: cannot open inp file ',self.inpFile
      return
    for line in fileinput.input(self.inpFile):
      matchSam = mySCIpattern.pattNml['options']['smpfile'].match(line)
      if matchSam:
        self.samFile = matchSam.group(2).replace("'","").strip()
        if len(self.samFile) > 1:
          if not os.path.exists(self.samFile):
            print 'Error: cannot find sam file ',self.samFile
            self.samFile = os.path.dirname(self.inpFile) + '/' + self.samFile
            print 'Checking for file ',self.samFile
            if not os.path.exists(self.samFile):
              print 'Error: cannot find sam file ',self.samFile
              return
        break
    fileinput.close()

  def readLogFile(self,mySCIpattern):
    nTerm = 0
    if os.path.exists(self.logFile):
      for line in fileinput.input(self.logFile):
        matchNterm = mySCIpattern.pattNterm.match(line)
        if matchNterm:
          nTerm = nTerm + 1
      fileinput.close()
    return nTerm
 
  def readNtvFile(self,ntvFile,mySCIpattern):
    print '\nPredicted source parameters from ',ntvFile,' :'
    for line in fileinput.input(ntvFile):
      matchRelTime = mySCIpattern.pattRelTime.match(line)      
      if matchRelTime:
        relTime = matchRelTime.group(3)
        print 'Release time = ',relTime        
      matchRelLoc = mySCIpattern.pattRelLoc.match(line)
      if matchRelLoc:
        (relX, relY) = map(float,(matchRelLoc.group(2), matchRelLoc.group(3)))
        print 'Release loc  : X = ',relX,' Y = ',relY
        break
    fileinput.close()
    (HH, MM, SS) = relTime.replace("Z","").split(':')
    relTime = float(HH) + float(MM)/60. + float(SS)/3600.
    print 'hr = ',relTime

    return(relTime,relX,relY)

  def readSumFile(self,sumFile,mySCIpattern):
    print '\nPredicted source parameters from ',sumFile,' :'
    massEst = False
    relT    = -999
    for line in fileinput.input(sumFile):
      if massEst:
        try:
          float(line.split()[0])
        except ValueError:
          continue
        (relT, relMass) = line.split()
        # Look for 0. release time
        if float(relT) < 1.e-6:
          break
      else:
        matchMassEst = mySCIpattern.pattMassEst.match(line)      
        if matchMassEst:
          massEst = True
    fileinput.close()

    if relT < -998:
      print 'Error: cannot find Release time 0. in ',sumFile
      relMass = None
    print 'Mass  = ',relMass
        
    return relMass

# class for creating sam file
class samList:

  def  __init__(self,samFile=None,samLoc=None,samHead=None,matList=None):
    self.samFile = samFile
    self.samLoc = samLoc
    self.samHead = samHead
    self.matList = []
    if matList:
      self.matList = matList

  def createSam(self,matList=None,samLoc=None,outKey=None):
    if len(self.samLoc) < 1:
      raise RuntimeError('Error: samLoc must not be empty')
    samOut = open(self.samFile,"w",0)
    samOut.write(self.samHead)
    nSen = 0
    if samLoc:
      self.samLoc  = self.samLoc + samLoc
    if matList:
      self.matList  = self.matList + matList
    for (xSrc,ySrc) in self.samLoc:
      for matName in self.matList:
        nSen += 1
        if not outKey:
          outKey = CONC
        samOut.write('%8.3f %8.3f %8.3f %s %s:1 Sensor%d\n'%(xSrc,ySrc,0.,outKey,matName,nSen))
    samOut.close()

# Function to copy inFile to outFile and change namelist based
# on dictionary KeyNml.
def chngNml(inFile,outFile,KeyNml,KeyPatt,tail):
 
  if outFile == inFile:
    outFile = 'TemporaryOut.tmp'

  if inFile.endswith(('.inp','.msc','.scn')):
    sfxes = ['',] 
  else:
    sfxes = ['.inp','.msc','.scn']
  
  for sfx in sfxes:
    inNewFile = inFile + sfx
    outNewFile = outFile + sfx
    if outNewFile.startswith("Append:"):
      outNewFile = outNewFile.replace("Append:","")
      nmlFile = open(outNewFile,"a",0)
    else:
      nmlFile=open(outNewFile,"w",0)     
    print '\nCopying %s to %s' % (inNewFile,outNewFile)
    for line in fileinput.input(inNewFile):
      delKeyList = []
      for nmlKey,nmlVal in KeyNml.iteritems():     
        # Replace nmlKey
        pattKey  = KeyPatt[nmlKey]    
        matchKey = pattKey.match(line)
        if matchKey:
          addNmlEnd = ''
          if line.strip().endswith('/'):
            addNmlEnd = '/'
          line = matchKey.group(1) + nmlVal + matchKey.group(3) + addNmlEnd + tail
          if nmlKey == 'metfile':
            nLen = len(line.strip().split('@')[1])
            line = matchKey.group(1) + '%03d'%nLen + nmlVal + matchKey.group(3) + tail
          if nmlKey == 'reltyp' and nmlVal == 'C':
            nmlFile.write(' %s%g,\n'%('TDUR = ',KeyNml['tdur']))
            print '%s = %s'%('TDUR',KeyNml['tdur'])
          print '%s = %s'%(nmlKey,nmlVal)
          delKeyList.append(nmlKey)
      nmlFile.write(line)
      for nmlKey in delKeyList:
        del KeyNml[nmlKey]
    fileinput.close()
    nmlFile.close()
    if outFile == 'TemporaryOut.tmp':
      # Replace the infile with outfile
      os.rename(outNewFile,inNewFile)
    if len(KeyNml) == 0:
      break

class Env:
  def  __init__(self):
    self.env = os.environ.copy()
    self.tail = None
    self.hpacstub = 'hpacstub'
    self.plotstub = 'plotstub'

def setEnv(myEnv=None,binDir=None,SCIPUFF_BASEDIR=None,compiler=None,version=None):
  if not myEnv:
    myEnv = Env()
  if sys.platform == 'win32':
    if not binDir:
      SCIPUFF_BASEDIR,version = os.path.split(binDir)
      SCIPUFF_BASEDIR,compiler = os.path.split(SCIPUFF_BASEDIR)
    else:
      if not SCIPUFF_BASEDIR:
        SCIPUFF_BASEDIR = "d:\SourceEstimation\Docs\Aamar\Paper2\Sources\bin"
      if not compiler:
        compiler = 'intel'
      if not version:
        version = 'release'
    OldPath = myEnv.env["PATH"]
    bindir = SCIPUFF_BASEDIR + "\\" + compiler + "\\" + version
    urbdir = SCIPUFF_BASEDIR + "\\" + compiler + "\\nonurban"  + "\\" + version
    vendir = SCIPUFF_BASEDIR + "\\vendor" 
    myEnv.env["PATH"] = "%s;%s;%s;%s" % (bindir,urbdir,vendir,OldPath)
    myEnv.hpacstub = ["hpacstub.exe","-I:","-M:10000"]
    myEnv.plotstub = ["plotstub.exe","-I:"]
    myEnv.tail = '\r\n'
  else:
    if binDir:
      SCIPUFF_BASEDIR = binDir
    else:
      if not SCIPUFF_BASEDIR:
        SCIPUFF_BASEDIR="/home/user/bnc/SourceEstimation/FilterTests/src/gitP2/UNIX/FULL/bin/linux/gfort"
    myEnv.env["SCIPUFF_BASEDIR"] = SCIPUFF_BASEDIR
    myEnv.env["LD_LIBRARY_PATH"] = "/usr/local/lf9562/lib:/home/user/bnc/gfortran/x86_32:/home/user/bnc/sqlite3/flibs-0.9/lib/gfort:/home/user/sid/HDF"
    myEnv.env["LD_LIBRARY_PATH"] = myEnv.env["LD_LIBRARY_PATH"] + ':' + SCIPUFF_BASEDIR
    myEnv.hpacstub  = ["%s/hpacstub" % SCIPUFF_BASEDIR,"-I:","-M:10000"]
    myEnv.plotstub  = ["%s/plotstub" % SCIPUFF_BASEDIR,"-I:"]
    myEnv.tail = '\n'
    print myEnv.env["LD_LIBRARY_PATH"]
  print 'Path = ',myEnv.env["PATH"]
  print myEnv.hpacstub
  return (myEnv)

def runSci(prjName,myEnv=None,binDir=None,templateName='',KeyNml=None,nFlt=30,rType='INST',createPrj=''):

  mySCIpattern = Pattern()

  if not myEnv:
    myEnv = Env()

  if binDir or not myEnv.tail:
    setEnv(myEnv,binDir=binDir)

  tail = myEnv.tail

  # Remove old output files
  pattDos = re.compile(".+\.dos\d+")
  inpList = ['inp','msc','scn','sen']
  outList = ['.smp','.log','.prj','.puf','.dos','.err','.rst']
  
  if len(templateName) > 0:
    cleanList = inpList + outList
  elif len(createPrj) == 0 or createPrj == "CRT:":
    cleanList = outList
  else:
    cleanList = None

  if cleanList:
    for fName in os.listdir('./'):
      if fName.startswith(prjName):
        for sfx in cleanList:
           if fName.endswith(sfx):
             print 'Deleting ',fName
           elif pattDos.search(fName):
             print 'Deleting ',fName
           else:
             continue
           try:
             os.remove(fName)
           except OSError as errMsg:
             print errMsg

  # Copy input files from template files
  if len(templateName) > 0:
    for sfx in inpList: 
      if os.path.exists(templateName+'.'+sfx):
        shutil.copy(templateName+'.'+sfx, prjName+'.'+sfx)
      else:
        print 'Warning: cannot find ',templateName+'.'+sfx

  #  Change namelists if requested
  if KeyNml:
    chngNml(prjName,prjName,KeyNml,mySCIpattern.pattNameList,tail)

  # Get run mode from inp file
  (nmlNames,nmlValues) = mySCIpattern.readNml(prjName+'.inp')
  i = nmlNames.index('flags')
  runMode = int(nmlValues[i]['run_mode'])
  print '\n run mode = ',runMode
  
  prjName = createPrj + prjName

  if runMode == 128:
    # Remove filtered.sen and set run type for reverse run
    try:
      os.remove('Filtered.sen')
    except OSError as errMsg:
      print errMsg
    # Check run type
    if rType == 'CONT':
      isCont = 'y' + tail 
    else:
      isCont = 'n' + tail 
    # Setup Inputs for reverse run
    Inputs = ('%s%s%s%d%s'% (prjName+tail,'y'+tail,isCont,nFlt,tail))
  else:
    # Setup Inputs for forward run
    Inputs = ('%s%s'% (prjName+tail,tail))

  # Run hpacstub
  run_cmd.Command(myEnv.env,myEnv.hpacstub,Inputs,tail)

# Main Program

if __name__ == '__main__':

  #inFile = raw_input('\nFilename? ')
  inFile   = 'temp.inp'
  #nmlName = raw_input('\nNamelist? ')
  nmlName = 'ctrl'
  mySCIpattern = Pattern()
  #print mySCIpattern.Nml[nmlName]
  #print mySCIpattern.pattNml[nmlName]
  (nmlNames,nmlValues) = mySCIpattern.readNml(inFile)
  for i in range(len(nmlNames)):
    print '\nNamelist = ',nmlNames[i]
    print nmlValues[i]
    #for key,value in nmlValues[i].items():
    #  print key,'=',value
 

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
          cPattern = str(r'(.*\b%s\s*=\s*)(.*?)($)'%vname)
          rPattern = re.compile(cPattern,re.I)
          if vname == 'metfile':
            rPattern = re.compile("(.*@)(\d{3}.+)(\s*.*)")
          if vname == 'smpfile':
            rPattern = re.compile("(.*%s\s*=\s*)(\S+)(\s*)(.*)"%vname,re.I)
            #print rPattern
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
    self.pattRelTime = re.compile("^Time(.+?):\s*(.+)")
    self.pattRelLoc  = re.compile("^Field max(.+):\s*(.+?)\s+(.+?)\s+(.+)")

    # ini file keywords
    self.pattSrcEst = re.compile(".*[SourceEstimation].*")
    self.maxHits    = re.compile(".*MaxAdjointHits=(\d+)")
    
    # sum file keywords
    self.pattLocFunc = re.compile("^\s*Location\s+Function(.*)")
    self.pattMassEst = re.compile("^\s*Mass\s+Estimate(.*)")
    self.pattDurEst  = re.compile("^\s*Duration\s+Estimate(.*)")

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
    # check if msc file and continue reading after 
    # end of met namelist for metfiles
    isMscFile = nmlFile.name.endswith('.msc') 
    for line in nmlFile:
      line = re.sub("\n","",line)
      line = re.sub("\r","",line)
      line.strip()
      matchStaNml = self.pattStaNml.match(line)
      matchEndNml = self.pattEndNml.match(line)
      if matchStaNml:
        #print 'match start'
        nmlLines = []
        nmlLines = self.addNml(line,nmlLines)
        nmlName = matchStaNml.group(1).lower()
        # Namelist ending on same line
        if matchEndNml:
          #print 'match end'
          isNml = False
          if isMscFile:
            continue
          else:
            break
        else:
          isNml = True
      if isNml and matchEndNml:
        #print 'match end'
        nmlLines = self.addNml(line,nmlLines)
        isNml = False
        if isMscFile:
          continue
        else:
          break
      if isNml and not matchStaNml:
        nmlLines = self.addNml(line,nmlLines)
      if isMscFile and len(nmlLines) > 0 and not isNml:
        if len(line) > 0:
          metFiles = line.split('@')
          for i in range(1,len(metFiles),2):
            nmlLines.append('METFILE = %s'%metFiles[i][3:])
          break
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
              #print key,":",matchNmlKey.group(2)
              nmlValue.update({key:matchNmlKey.group(2)})
          if nameList == 'met':
            if line.startswith('METFILE'):
              metFname = line.split('=')[1].strip()
              nmlValue.update({'metfile':metFname})
        nmlValues.append(nmlValue)
      else:
        nmlFile.close()
        break
    return(nmlNames,nmlValues)
  
# class for reading releases
class RelList(object):

  def  __init__(self):
    self.rlsList = []

  def getRelList(self,mySCIpattern,scnFile):
    (nmlNames,nmlValues) = mySCIpattern.readNml(scnFile)
    for i in range(len(nmlNames)):
      relDat = {}
      for key in ['relmat','reltyp','trel','xrel','yrel','zrel','cmass','sigx','sigy','sigz','tdur']:
        #print key,nmlValues[i][key]
        relDat.update({key:nmlValues[i][key]})
      self.rlsList.append(relDat)
                   
class Files(object):

  def __init__(self,prjName,mySCIpattern=None,samFile=None):

    self.prjName = prjName
    if mySCIpattern is None:
      mySCIpattern = Pattern()
    self.SCIpattern = mySCIpattern
    #print prjName

    # input files
    self.inpFile = self.prjName + '.inp'
    self.mscFile = self.prjName + '.msc'
    self.scnFile = self.prjName + '.scn'
    self.inpList = dict([('inp',self.inpFile),('msc',self.mscFile),('scn',self.scnFile)])

    # release list
    self.relList = RelList()
      
    # output file
    self.prjFile = self.prjName + '.prj'
    self.logFile = self.prjName + '.log'
    self.pufFile = self.prjName + '.puf'
    self.smpFile = self.prjName + '.smp'
 
    if samFile is None:
      # Read sam file from inpfile
      #print 'call getSamFile'
      self.getSamFile()
    else:
      self.samFile = samFile

  def getSamFile(self):
    self.samFile = None
    if not os.path.exists(self.inpFile):
      print 'Error: cannot open inp file ',self.inpFile
      return
    for line in fileinput.input(self.inpFile):
      matchSam = self.SCIpattern.pattNml['options']['smpfile'].match(line)
      #if 'SMPFILE' in line:
        #print self.SCIpattern.pattNml['options']['smpfile']
        #print line
        #print matchSam
        #print matchSam.span(),matchSam.group(2)
      if matchSam:
        self.samFile = matchSam.group(2).replace("'","").replace(",","").strip()
        #print 'SAMFILE = "',self.samFile,'"'
        if len(self.samFile) > 1:
          if not os.path.exists(self.samFile):
            print 'Error: cannot find sam file ',self.samFile
            self.samFile = os.path.join(os.path.dirname(self.inpFile),self.samFile)
            print 'Checking for file ',self.samFile
            if not os.path.exists(self.samFile):
              print 'Error: cannot find sam file ',self.samFile
              break
        else:
          self.samFile = None
        break
    fileinput.close()

  def readLogFile(self):
    nTerm = 0
    if os.path.exists(self.logFile):
      for line in fileinput.input(self.logFile):
        matchNterm = self.SCIpattern.pattNterm.match(line)
        if matchNterm:
          nTerm = nTerm + 1
      fileinput.close()
    return nTerm
 
  def readNtvFile(self,ntvFile):
    #print '\nPredicted source parameters from ',ntvFile,' :'
    for line in fileinput.input(ntvFile):
      matchRelTime = self.SCIpattern.pattRelTime.match(line)      
      if matchRelTime:
        relTime = matchRelTime.group(2)
        #print 'Release time = ',relTime        
        continue
      matchRelLoc = self.SCIpattern.pattRelLoc.match(line)
      if matchRelLoc:
        (relX, relY) = map(float,(matchRelLoc.group(2), matchRelLoc.group(3)))
        #print 'Release loc: X = ',relX,', Y = ',relY
        break
    fileinput.close()
    if 'Z' in relTime:
      Hr = None
      if '(' in relTime:
        Hr,relTime = relTime.split('(')
        relTime    = relTime.split()[1].replace(")","")
      (HH, MM, SS) = relTime.replace("Z","").split(':')
      if Hr is None:
        relTime = float(HH) + float(MM)/60. + float(SS)/3600.
      else:
        relTime = str(float(HH) + float(MM)/60. + float(SS)/3600.) + '(%8.3f Hr)'%float(Hr)        

    return(relTime,relX,relY)

  def readSumFile(self,sumFile,showDate=False,getList=False):
    #print '\nPredicted source parameters from ',sumFile,' :'
    pName = [sLoc,sMas,sDur] = [0,1,2]
    estList = [[] for i in pName]
    maxList = [[-999,'None'] for i in pName]
    pattDurUnt = re.compile("^\s*Duration\s*\((.*)\).*")
    section = -1
    for line in fileinput.input(sumFile):
      matchLocFunc = self.SCIpattern.pattLocFunc.match(line)      
      matchMassEst = self.SCIpattern.pattMassEst.match(line)      
      matchDurEst  = self.SCIpattern.pattDurEst.match(line)      
      if matchLocFunc or matchMassEst or matchDurEst:
        section += 1
        if matchMassEst:
          maxList[sMas][1] = matchMassEst.group(1).strip().replace('(','').replace(')','')
        continue
      try:
        float(line.split()[0])
      except ValueError:
        if line[:4] == ' t -':
          if showDate:
            tMax = line.split()[2:4]
          else: 
            tMax = line.split()[3]
        elif 'Duration' in line:
          matchDurUnt = pattDurUnt.match(line)      
          maxList[sDur][1] = matchDurUnt.group(1)
        continue
      relT, relPrm = map(float,line.split())
      estList[section].append([relT,relPrm])
    fileinput.close()
    for i in pName:
      if i < sDur:
        for relT,relP in estList[i]:
          # Look for 0. release time
          if relT < 1.e-6:
            maxList[i][0] = relP
            break
      else:
        for durT,relP in estList[i]:
          # Look for min release time
          if abs(relP-maxList[sLoc][0]) < 1.e-10:
            maxList[sDur][0] = durT
            break
    if getList:
      return (tMax,estList)
    else:
      return (tMax,maxList)

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
          outKey = 'CONC'
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
          if nmlKey == 'metfile':
            metFiles = nmlVal.strip().split(';')
            line = ''
            for metFile in metFiles:
              nLen = len(metFile.strip())
              line += '   1 @%03d'%nLen + metFile.strip()
            line += tail
          else:
            line = matchKey.group(1) + nmlVal + matchKey.group(3) + addNmlEnd + tail
             
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
      if sys.platform == 'win32':
        shutil.move(outNewFile,inNewFile)
      else:
        os.rename(outNewFile,inNewFile)
      print outNewFile,' -> ',inNewFile
      
    if len(KeyNml) == 0:
      break

class Env:
  def  __init__(self):
    self.env = os.environ.copy()
    self.tail = None
    self.runsci = 'runsci'
    self.scipp    = 'scipp'

def setEnv(myEnv=None,binDir=None,SCIPUFF_BASEDIR=None,iniFile=None,\
           compiler=None,version=None,platform=None):
  if myEnv is None:
    myEnv = Env()
  if iniFile is not None:
    iniFile = "-I:" + iniFile
  else:
    iniFile = "-I:" 
  if sys.platform == 'win32':
    if binDir is not None:
      SCIPUFF_BASEDIR,version = os.path.split(binDir)
      SCIPUFF_BASEDIR,compiler = os.path.split(SCIPUFF_BASEDIR)
    else:
      # set default directories
      if SCIPUFF_BASEDIR is None:
        SCIPUFF_BASEDIR = "d:\\hpac\\gitP2\\bin"
      if compiler is None:
        compiler = 'intel'
      if version is None:
        version = 'release'
    #OldPath = myEnv.env["PATH"]
    bindir = SCIPUFF_BASEDIR + "\\" + compiler + "\\" + version
    binDirLwr = bindir.lower()
    if 'workspace' in binDirLwr:
      baseDir =  binDirLwr[:binDirLwr.index('workspace')-1]
      if platform is None:
        platform = 'win32'
      vendir = baseDir + "\\bin\\vendor\\" + platform
      myEnv.env["PATH"] = "%s;%s" % (bindir,vendir)
    else: 
      urbdir = SCIPUFF_BASEDIR + "\\" + compiler + "\\urban"  + "\\" + version
      nurdir = SCIPUFF_BASEDIR + "\\" + compiler + "\\nonurban"  + "\\" + version
      vendir = SCIPUFF_BASEDIR + "\\vendor" 
      myEnv.env["PATH"] = "%s;%s;%s;%s" % (bindir,nurdir,urbdir,vendir)
    myEnv.runsci = [bindir+"\\runsci.exe",iniFile,"-M:10000"]
    myEnv.scipp = [bindir+"\\scipp.exe",iniFile]
    myEnv.tail = '\r\n'
  else:
    if binDir is not None:
      SCIPUFF_BASEDIR = binDir
    else:
      if SCIPUFF_BASEDIR is not None:
        SCIPUFF_BASEDIR="/home/user/bnc/SourceEstimation/FilterTests/src/gitP2/UNIX/FULL/bin/linux/gfort"
    myEnv.env["SCIPUFF_BASEDIR"] = SCIPUFF_BASEDIR
    myEnv.env["LD_LIBRARY_PATH"] = "/usr/local/lf9562/lib:/home/user/bnc/gfortran/x86_32:/home/user/bnc/sqlite3/flibs-0.9/lib/gfort:/home/user/sid/HDF"
    myEnv.env["LD_LIBRARY_PATH"] = myEnv.env["LD_LIBRARY_PATH"] + ':' + SCIPUFF_BASEDIR
    myEnv.runsci  = ["%s/runsci" % SCIPUFF_BASEDIR,iniFile,"-M:10000"]
    myEnv.scipp  = ["%s/scipp" % SCIPUFF_BASEDIR,iniFile]
    myEnv.tail = '\n'
    print myEnv.env["LD_LIBRARY_PATH"]
  print 'Path = ',myEnv.env["PATH"]
  print myEnv.runsci
  return (myEnv)

def readKeyNml(nmlFile):
  KeyNml = {}
  print '\nReading new namelist values from file ',nmlFile
  if os.path.exists(nmlFile):
    for line in fileinput.input(nmlFile):
      if len(line.strip()) > 1:
        key,value = line.strip().split('=')
        key = key.strip()
        value = value.strip().replace(' ','')
        if key != 'metfile':
          value += ','
        KeyNml.update({key.strip():value.strip()})
    fileinput.close()
    print '  New values - '
    for key in KeyNml:
      print '    ',key,':',KeyNml[key]
  else:
    print 'Error: Cannot find namelist value file'
  return KeyNml

def runSci(prjName,myEnv=None,binDir=None,templateName='',inpList=None,KeyNml=None,nFlt=30,rType='INST',createPrj='',outOut=False):

  mySCIpattern = Pattern()

  if myEnv is None:
    myEnv = Env()

  if binDir is not None or myEnv.tail is None:
    setEnv(myEnv,binDir=binDir)

  tail = '\r\n' #myEnv.tail

  print '\nPATH = ',myEnv.env["PATH"],'\n'

  # Remove old output files
  pattDos = re.compile(".+\.dos\d+")
  if inpList is None:
    inpList = ['inp','msc','scn','sen']
  outList = ['.smp','.log','.prj','.puf','.dos','.err','.rst','.smp.db']
  
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
  if KeyNml is not None:
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
    #Inputs = ('%s%s%d%s'% (prjName+tail,isCont,nFlt,tail))
    Inputs = os.linesep.join(["prjName","n",str(nFlt),""]).encode("utf-8")
  else:
    # Setup Inputs for forward run
    Inputs = ('%s%s'% (prjName+tail,tail))

  # Run runsci
  
  print 'Inputs = ',Inputs
  #myEnv.runsci.append(' >run.log')
  #myEnv.runsci = ['c:\\cygwin\\bin\\echo','testing']
  run_cmd.Command(myEnv.env,myEnv.runsci,Inputs,tail,outOut=outOut)

# Main Program

if __name__ == '__main__':

  #os.chdir("d:\\SrcEst\\P2\\runs\\120627\\ETEX")
  #prjName = 'rev_etex_f010'
  os.chdir('d:\\SCIPUFF\\runs\\EPRI\\aermod\\Bowline\\SCICHEM')
  prjName = 'bowline_ss'
  #os.chdir("/home/user/bnc/scipuff/runs/EPRI/tva/tva_980825/SCICHEM-2012")
  #prjName = 'tva_980825'
  mySCIfiles = Files(prjName)
  print '\n samFile = "',mySCIfiles.samFile,'"\n'
  #mySCIfiles.relList.getRelList(mySCIfiles.SCIpattern,mySCIfiles.scnFile)
  #print mySCIfiles.relList.rlsList
  #nmlName = raw_input('\nNamelist? ')
  #nmlName = 'scn'
  #print mySCIpattern.Nml[nmlName]
  #print mySCIpattern.pattNml[nmlName]
  #inFile = raw_input('\nFilename? ')
  #inFile   = 'rev_etex_f010.scn'
  #(nmlNames,nmlValues) = mySCIpattern.readNml(inFile)
  #for i in range(len(nmlNames)):
    #print '\nNamelist = ',nmlNames[i]
    #print nmlValues[i]
    #for key,value in nmlValues[i].items():
    #  if key == 'relmat':
    #    print key,'=',value
 

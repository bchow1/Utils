def setEnv(myEnv):
  if sys.platform == 'win32':
    SCIPUFF_BASEDIR = "d:\SourceEstimation\Docs\Aamar\Paper2\Sources\bin"
    compiler = 'intel'
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
    #SCIPUFF_BASEDIR="/usr/pc/biswanath/SourceEstimation/Docs/Aamar/Paper2/Sources/UNIX/FULL/bin/linux/gfort"
    SCIPUFF_BASEDIR="/home/user/bnc/SourceEstimation/Docs/Aamar/Paper2/Sources/UNIX/FULL/bin/linux/gfort"
    myEnv.env["SCIPUFF_BASEDIR"] = SCIPUFF_BASEDIR
    myEnv.env["LD_LIBRARY_PATH"] = "/usr/local/lf9562/lib:/home/user/bnc/gfortran:/home/user/bnc/sqlite3/flibs-0.9/lib/gfort:/home/user/sid/HDF"
    myEnv.env["LD_LIBRARY_PATH"] = myEnv.env["LD_LIBRARY_PATH"] + ':' + SCIPUFF_BASEDIR
    myEnv.hpacstub  = ["%s/hpacstub" % SCIPUFF_BASEDIR,"-I:","-M:10000"]
    myEnv.plotstub  = ["%s/plotstub" % SCIPUFF_BASEDIR,"-I:"]
    myEnv.tail = '\n'
    print myEnv.env["LD_LIBRARY_PATH"]
  print 'Path = ',myEnv.env["PATH"]
  print myEnv.hpacstub
  return (myEnv)

def runSci(myEnv,prjName,templateName='',KeyNml=None,nFlt=30,rType='INST',createPrj=''):

  global mySCIpattern

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
    SCI.chngNml(prjName,prjName,KeyNml,mySCIpattern.pattNameList,tail)

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

    if rType == 'CONT':
      isCont = 'y' + tail 
    else:
      isCont = 'n' + tail 

    Inputs = ('%s%s%s%d%s'% (prjName+tail,'y'+tail,isCont,nFlt,tail))

  else:

    Inputs = ('%s%s'% (prjName+tail,tail))

  run_cmd.Command(myEnv.env,myEnv.hpacstub,Inputs,tail)

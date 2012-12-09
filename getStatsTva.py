
#!/bin/env python
import os
import sys
import socket
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import sqlite3

compName = socket.gethostname()

# Local modules
if compName == 'sm-bnc' or compName == 'sage-d600':
  sys.path.append('C:\\cygwin\\home\\sid\\python')
if  compName == 'pj-linux4':
  sys.path.append('/home/user/bnc/python')
  
import utilDb
import setSCIparams as SCI

# Code for SCICHEM 2012 plots

def mainProg(prjName=None,obsPfx=None,preCur1=None,preCur2=None,prePfx2=None):

  if prjName is None:
    print "Must provide project name"
    return
  else:
   print 'prjName = ',prjName
  
  varNames = ["SO2", "O3", "NOx",  "NOy"]

  if "tva_990715" in prjName:
    distance = [16, 62, 106]
    times    = [11.5, 12.5, 17.0]
    zSmp     = [415, 584, 582]

  if "tva_980825" in prjName:
    distance = [20, 55, 110]
    times    = [12, 12.75, 14.5]
    zSmp     = [520, 600, 620]
    
  if "tva_980826" in prjName:
    distance = [18, 27, 86, 59, 93, 126]
    times    = [10.25, 10.5, 12, 12.5, 12.75, 13]
    zSmp     = [465, 500, 659, 910, 819, 662]
    
  if "tva_990706" in prjName:
    distance = [11, 31, 65]#, 91]
    times    = [12.0, 13.5,14.5, 16.75]#12.25, 13.0, 14.0, 16.75]
    zSmp     = [501, 505, 500, 533]
  
  avgObsDb = prjName + "avgObs.db" 
  avgObsConn = sqlite3.connect(avgObsDb)
  avgObsConn.row_factory = sqlite3.Row
  avgObsCur = avgObsConn.cursor()
  ccolor  = [ 'red', 'blue', 'green', 'cyan', 'magenta', 'lime', 'olive', 'maroon', 'teal', 'purple', 'aqua', 'navy', 'fuchsia']
      
  for idt,dist in enumerate(distance): 
    lArc = 2.*dist*np.pi/180.
    tblName = "dist" + str(dist)
    
    avgObsCur.execute('DROP table if exists %s'%tblName)
    createStr = "CREATE table %s( TRID integer,\
                TRdist integer, PlumeKM real, species varchar(8), conc real)"%tblName
    avgObsCur.execute(createStr)
    
    for varName in varNames:
       # Set Omax to zero for max plume no.
      if varName == 'SO2':
        oMax  = [0 for i in range(13)]

      # Observations
      # Observed data
      if "tva_990715" in prjName:
        if dist == 16:
          pls = [1,2,3,4]
        if dist == 62:
          pls = [6,7,8]
        if dist == 106:
          pls = [9,10,11]

      if "tva_980825" in prjName:
        if dist == 20:
          pls = [3,4,5]
        if dist == 55:
          pls = [6] #[6,7,8]
        if dist == 110:
          pls = [9,10,11]
          
      if "tva_990706" in prjName:
        if dist == 11:
          pls = [1,2,3,4,5]
        if dist == 31:
          pls = [6,7,8]
        if dist == 65:
          pls = [9,10,11]
        if dist == 89:
          pls = [12] 
        
        for ipl in pls:
          
          obsDbName = obsPfx + str(dist) + 'km_obs' + str(ipl) + '.csv.db'
          print '\n obsDbName = ',obsDbName
          obsConn = sqlite3.connect(obsDbName)
          obsConn.row_factory = sqlite3.Row
          obsCur = obsConn.cursor()
          # Observations
          if "tva_990706" in prjName:
            obsQry = 'select TRID, CAST(plumeKM as real), ' + varName + '/1000 from dataTable where plumeKM > -9998.'
          else:
            obsQry = 'select TRID, CAST(plumeKM as real), ' + varName + ' from dataTable where plumeKM > -9998.'
          print obsQry
          obsArray = utilDb.db2Array(obsCur, obsQry)
          if ipl == min(pls):
            plt.clf()
            plt.hold(True)
          plt.scatter(obsArray[:,1],obsArray[:,2],color=ccolor[ipl],marker='o')
          if varName == 'SO2':
             oMax[ipl] = np.where(obsArray[:,2] == obsArray[:,2].max())[0][0]
             print 'Max Obs SO2 at x index = ', oMax[ipl],' with x, value = ',obsArray[oMax[ipl],1],obsArray[oMax[ipl],2]

          maxDist = obsArray[oMax[ipl],1]
          for i in range(len(obsArray)):
            # Set x values where SO2 max to obs x value for plume ip1
            obsArray[i,1] = obsArray[i,1] - maxDist 
          plt.scatter(obsArray[:,1],obsArray[:,2],color=ccolor[ipl],marker='d')
          inStr = "INSERT into %s values("%tblName
          for myrow in obsArray:
            insertStr = inStr + '%d, %5.2f, %5.3f, "%s", %g)'%(myrow[0],dist,myrow[1],varName,myrow[2])
            #print insertStr
            avgObsCur.execute(insertStr) 
          #obsArray = obsCur.execute(obsQry)
            
          avgObsConn.commit()
          
      avgQry = 'select round(plumeKM), avg(conc) from %s where species="%s" and conc >= 0 and plumeKM >-999 group by round(plumeKM)'%(tblName,varName)
      #print avgQry
      AveArray2 = utilDb.db2Array(avgObsCur,avgQry)
      #print AveArray2
      #plt.axis([0.0,500.0,0,20])
      plt.plot(AveArray2[:,0], AveArray2[:,1],marker='*')
      plt.hold(False) 
      plt.show()
  sys.exit()
                
  for idt,dist in enumerate(distance): 

    if preCur2 is None:
      if prePfx2 is None:
        print "Must provide prefix for SCICHEM-01 prediction"
        return
      # Predictions SCICHEM-01
      pre2DbName =  prePfx2 + '_' + str(dist) + 'km' + '.csv.db'       
      print 'Predicted DB SCICHEM99', pre2DbName
      preConn2 = sqlite3.connect(pre2DbName)
      preConn2.row_factory = sqlite3.Row
      preCur2 = preConn2.cursor()
      print preConn2
    
    lArc = 2.*dist*np.pi/180.
    
    
    for varName in varNames:

      print '\n',dist,' km, ',varName
      
      # Prediction query
      if varName == "NOx":
        preQry1 = 'select xSmp,Sum(Value) from samTable a,smpTable p where a.colNo=p.colNo'
        preQry1 += " and varName in ('NO2', 'NO' ) "
        preQry1 += " and zSmp = %f and time = %3f group by smpId"%(zSmp[idt],times[idt])
      elif varName == 'NOy':
        preQry1 = "select xSmp,Sum(Value) from samTable a,smpTable p where a.colNo=p.colNo"
        preQry1 += " and varName in ('NO2','NO','NO3','N2O5','HNO3','HONO','PAN'  ) "
        preQry1 += " and zSmp = %f and time = %3f group by smpId"%(zSmp[idt],times[idt])
      else:  
        preQry1  = "select xSmp,Value from samTable a,smpTable p where a.colNo=p.colNo and "
        preQry1 += "varName = '%s' and zSmp = %f and time = %3f order by smpId"%(varName,zSmp[idt],times[idt])      
      print preCur1, preQry1
      
      # Predictions #1 (2012)
      preArray1 = utilDb.db2Array(preCur1,preQry1)
      if varName == 'SO2':
        # Set x index where SO2 is max. Same for all obs plumes
        iMax1 = np.where(preArray1[:,1] == preArray1[:,1].max())[0][0]
          
      # Predictions #2 (v2100)
      if prePfx2 is None:
        preArray2 = utilDb.db2Array(preCur2,preQry1)
      else:
        preQry2 = 'select dist, ' + varName + ' from dataTable'
        preArray2 = utilDb.db2Array(preCur2,preQry2)
        
      if varName == 'SO2':
        # Set x index where SO2 is max. Same for all obs plumes
        iMax2 = np.where(preArray2[:,1] == preArray2[:,1].max())[0][0]
                   
      # Set Omax to zero for max plume no.
      if varName == 'SO2':
        oMax  = [0 for i in range(12)]

      figSave = 0
      #obsAvg = 
           
      #insertQry = 'Insert into speciesConc ('+ ipl, obsArray[0],obsArray[1],obsArray[2], obsArray[4]
      #print insertQry
      if varName == 'SO2':
        oMax[ipl] = np.where(obsArray[:,1] == obsArray[:,1].max())[0][0]
        print 'Max Obs SO2 at x index = ', oMax[ipl],' with x, value = ',obsArray[oMax[ipl],0],obsArray[oMax[ipl],1]


      print '\nFor varName %s, plume no. %d,x index = %d, x = %f ,conc = %f\n'%\
            (varName,ipl,oMax[ipl],obsArray[oMax[ipl],0],obsArray[oMax[ipl],1])
      
      if figSave:
        # Align the prediction1 and observed centerlines
        for i in range(len(preArray1)):
          # Set x values where SO2 max to obs x value for plume ip1
          preArray1[i,0] = float(i-iMax1)*lArc + obsArray[oMax[ipl],0]
          if i == iMax1:
            print 'Adjusted preArray1 x,c = ',preArray1[i,:] 
          

        # Align the prediction2 and observed centerlines

        for i in range(len(preArray2)):
          # Set x values where SO2 max to obs x value for plume ip1
          preArray2[i,0] = float(i-iMax2)*lArc + obsArray[oMax[ipl],0] 
          if i == iMax2:
            print 'Adjusted preArray2 x,c = ',preArray2[i,:]
         
        # Plot
        
        #figName  = str(dist) +'km_' +varName +'_'+ str(times[idt]) + 'hr_obs' + str(ipl) + '.png'
        figName  = str(dist) +'km_' +varName +'_'+ str(times[idt]) + 'hr.png'
        #figTitle = '%s (@ %d km for plume %d)'%(varName,dist,ipl)
        figTitle = '%s (@ %d km)'%(varName,dist)
        
        print figName, varName, str(ipl)

        print varName , figSave, ipl, len(pls), 
        ##pltCmpConc(dist, varName, obsArray, preArray1, preArray2, figTitle, figName, figSave)
        

        obsConn.close()
    if prePfx2 is not None:
      print 'preConn2 is still open'
      #preConn2.close()
          
  return

def initDb():
  #print len(colNames),colNames
  dbFile =  'tva_master.db'
  dbConn = sqlite3.connect(dbFile)
  dbCur = dbConn.cursor() 
  return (dbCur,dbConn)

def insertDb(dbCur,nCol,colTypes,colValues):
  insertStr = 'INSERT into dataTable VALUES('
  for i in range(nCol):
    if colTypes[i] == 'string':
      insertStr += "'" + colValues[i] + "'"
    else:     
      if len(colValues[i]) < 1:
        colValues[i] = '-9999'
      else:
        try:
          colValue = ast.literal_eval(colValues[i].strip())
          if (not isinstance(colValue,int) and \
              not isinstance(colValue,float)):
            colValues[i] = '-9999'
        except ValueError:
          colValues[i] = '-9999'
        except SyntaxError:
          colValues[i] = '-9999'
      insertStr += colValues[i]
    if i == nCol-1:
      insertStr += ')'
    else:
      insertStr += ', '
  #print insertStr
  dbCur.execute(insertStr)
  return
          
def pltCmpConc(dist, varName, obsData, preData1, preData2, figTitle, figName, figSave):
  #import pdb; pdb.set_trace()
    # Set up plot parameters
  params1 = {'axes.labelsize': 10, 'text.fontsize': 10, 'xtick.labelsize': 10,
                'ytick.labelsize': 10, 'legend.pad': 0.1,  
                'legend.fontsize': 8, 'lines.markersize': 6, 'lines.width': 2.0,
                'font.size': 10, 'text.usetex': False}
  plt.rcParams.update(params1)
  print figName
  fig = plt.figure()
  if figSave == 1:
    plt.clf()
  fig.hold(True)
  lgndList = []
  ax = fig.add_subplot(111)
  #print obsData[:,1]
  if varName == 'O3':
    fac = 1
    if obsData is not None:
     cO = max(obsData[-1,1],obsData[0,1])
    if preData1 is not None:
      c1 = max(preData1[-1,1],preData1[0,1])
    if preData2 is not None:
     c2 = max(preData2[-1,1],preData2[0,1])
  else:
    fac = 1
    if obsData is not None:
     cO = min(obsData[-1,1],obsData[0,1])
    if preData1 is not None:
     c1 = min(preData1[-1,1],preData1[0,1])
    if preData2 is not None:
     c2 = min(preData2[-1,1],preData2[0,1])
  if obsData is not None:
    C = obsData[:,1] - fac*cO
    LhO  = plt.plot(obsData[:,0],C,linestyle='None',marker='o',markersize=6,markerfacecolor='green') 
    LkO  = 'OBS'
    lgndList.append(LkO)
  if preData1 is not None: 
    C = ma.masked_where(preData1[:,1]<0.,preData1[:,1]) - fac*c1
    LhP1 = plt.plot(preData1[:,0],C,linestyle='-',color='red',marker='s',markersize=6,markerfacecolor='red')
    LkP1 = 'SCICHEM-2012'
    lgndList.append(LkP1)
  if preData2 is not None:
    C = ma.masked_where(preData2[:,1]<0.,preData2[:,1]) - fac*c2
    LhP2 = plt.plot(preData2[:,0],C,linestyle='-',color='cyan',marker='^',markersize=6,markerfacecolor='blue')
    LkP2 = 'SCICHEM-99'
    lgndList.append(LkP2)
  if figSave:
    plt.ylabel('Perturbation Concentration (ppm)')
    plt.xlabel('Cross plume distance (km)')
    plt.title(figTitle)
  if dist < 21:
    plt.xlim([-20,20])
  else:
    plt.xlim([-50,50])
  #if varName == 'O3':
  #  plt.ylim([0,0.1])
  if figSave == 1:
    plt.legend([LkO,LkP1,LkP2],bbox_to_anchor=(0.02,0.98),loc=2,borderaxespad=0.)
    lgnd  = plt.gca().get_legend()
    ltext = lgnd.get_texts()
    plt.setp(ltext,fontsize=9)
    fig.hold(False)
    plt.savefig(figName)
  else:
    fig.hold(True)
  #sys.exit()
  #plt.show()
  return

def getSmpDb(prjName):
    mySciFiles = SCI.Files(prjName)
    smpDb = '%s.smp.db'%(prjName)
    print '%%%%%%%%%%%%', smpDb
    # Create database for calculated data 
    ## print 'Create smpDb ',smpDb,' in ',os.getcwd()
    (smpDbConn,smpDbCur,smpCreateDb) = utilDb.Smp2Db(smpDb,mySciFiles)
    return (smpDbConn,smpDbCur)

            
# Main program
if __name__ == '__main__':

  if compName == 'sm-bnc':
    #runDir='d:\\SCIPUFF\\runs\\EPRI\\Nash99'
    #runDir='d:\\SCICHEM-2012\\TVA_990715'
    runDir = 'd:\\scipuff\\runs\EPRI\\tva_980825'
  if compName == 'pj-linux4':
    #runDir = '/home/user/bnc/scipuff/runs/EPRI/tva/tva_980825'
    runDir = '/home/user/bnc/scipuff/EPRI_121001/runs/tva/tva_990715'
  if compName == 'sage-d600':
    runDir = 'D:\\SCICHEM-2012\\TVA_990706' 
  os.chdir(runDir)

  print 'runDir = ',runDir

  # Observed data 
  obsPfx = os.path.join('OBS','tva_070699_')
  #obsPfx = os.path.join('OBS','cumb2_')
  print obsPfx

  # Predicted SCICHEM-2012 data
  prjName1 = os.path.join('SCICHEM-2012','tva_990706')
  print '**********' , 
  prjName1
  preConn1,preCur1 = getSmpDb(prjName1)

  # Predicted SCICHEM-01 data
  prjName2 = os.path.join('SCICHEM-01','070699_vo3_lin_intel')
  #prjName2 = os.path.join('SCICHEM-01','TVA_990706')
  preConn2,preCur2 = getSmpDb(prjName2)
  print prjName2
  
  # Use prePfx2 + '_' + str(dist) + 'km' + '.csv.db'
  #prePfx2 = os.path.join('SCICHEM-01','cumb2')
  #prePfx2 = os.path.join('SCICHEM-01','TVA_082598')
  prePfx2 = None

  mainProg(prjName=prjName1,obsPfx=obsPfx,preCur1=preCur1,preCur2=preCur2,prePfx2=prePfx2)

  #preConn1.close()
  #preConn2.close()

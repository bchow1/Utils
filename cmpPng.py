#
import os
import sys
import optparse
import numpy as np
import matplotlib.pyplot as plt
#

def joinPDF(flist,fname):

  import subprocess

  command = [["gs","-dBATCH","-dNOPAUSE","-q","-sDEVICE=pdfwrite","-sOutputFile=%s" % fname],\
             ["rm","-f"]]
  for cmd in command:
    cmd.extend(flist)
    (output, errmsg) = subprocess.Popen(cmd,stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE).communicate()
    if len(errmsg) > 0:
      print 'output = %s' % output
      print 'errmsg = %s' % errmsg
    else:
      if cmd == command[0]:
        print 'Combining output pdf files to create %s\n' % fname
  flist = []
  return flist

if __name__ == '__main__':

  # Parse arguments
  arg = optparse.OptionParser()
  arg.add_option("-d",action="store",type="string",dest="dir1")
  arg.add_option("-r",action="store",type="string",dest="dir2")
  arg.add_option("-i",action="store",type="string",dest="imgList")
  arg.add_option("-n",action="store_true",dest="png")
  arg.set_defaults(dir1=None,dir2=None,imgList=None)
  opt,args = arg.parse_args()

  if opt.dir1 is None or opt.dir2 is None:
    print 'Error: dir1 and dir2 must be specified and script must be run in Outputs directory'
    print 'Usage: cmpPng.py -d dir1 -r dir2 [-i img1[:img2]] [-n (png)]'
    sys.exit()
    #opt.dir1    = '111118.1900_testuserA'
    #opt.dir2    = '140307.2245'
    #opt.imgList = 'spore:PGT'

  if opt.png :
    isPDF = False
  else:
    isPDF = True

  print isPDF

  dir1    = opt.dir1
  dir2    = opt.dir2
  cDir    = os.getcwd()
  dirList = [dir1,dir2]
  for dNo,dName in enumerate(dirList):
    if dName.startswith('/'):
      dirList[dNo] = os.path.join(dName) 
    else:
      if dName.startswith('.'):
        os.chdir(os.path.join(cDir,dName))
        dirList[dNo] = os.getcwd()
        os.chdir(cDir)
      else:
        dirList[dNo] = os.path.join(cDir,dName,'Plots') 
  (dir1,dir2) = (dirList[0],dirList[1])

  print dir1, dir2

  if opt.imgList is None: 
    fList = os.listdir(dir1)
  else:
    fList = opt.imgList.split(':')
    for fNo,fName in enumerate(fList):
      if not fName.endswith('.png'):
        fList[fNo] = fName + '.png'

  imgList = []
  for fName in fList:
    if fName.endswith('.png'):
      if os.path.exists(os.path.join(dir2,fName)):
        #print 'Adding ',fName,' to list'
        imgList.append(fName)
      else:
        print 'Missing ',fName,' in ',dir2

  if len(imgList) == 0:
    print 'Error: Cannot find any png files in ',dir1

  print imgList

  os.chdir(dir1)

  if isPDF:
    joinList = []

  for imgNo,imgName in enumerate(imgList):
    fig = plt.figure(facecolor='white')
    fig.hold(True) 
    for dNo,dName in enumerate(dirList):
      ax = fig.add_subplot(1,2,dNo+1)
      imgFile = os.path.join(dName,imgName)
      im = plt.imread(imgFile)
      #print np.shape(im)
      # Only for color images
      #im[:,:,-1] = .7
      plt.gray()
      plt.imshow(im,interpolation='nearest',aspect='auto')
      plt.setp(plt.gca(), frame_on=False, xticks=(), yticks=())
      plt.title('Date: %s'%dName.split(os.path.sep)[-2])
    fig.hold(False) 
    if isPDF:
      imgList[imgNo] = 'cmp_' + imgName.replace('.png','') + '.pdf'
    else:
      imgList[imgNo] = 'cmp_' + imgName
    print imgList[imgNo]
    if isPDF:
      plt.savefig(imgList[imgNo],facecolor=fig.get_facecolor(),transparent=True,dpi=300) # pdf
      joinList.append(imgList[imgNo])
    else:
      plt.savefig(imgList[imgNo],facecolor=fig.get_facecolor(),transparent=True,dpi=600)  # png

  if isPDF:
    d1 =  dir1.split(os.path.sep)[-2]
    d2 =  dir2.split(os.path.sep)[-2]
    joinPDF(joinList,'cmp_%s_%s.pdf'%(d1,d2))

  print 'Creating in %s'%(dir1)
  os.chdir(cDir)

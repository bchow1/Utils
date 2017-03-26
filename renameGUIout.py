#!/bin/python
import os

fList = os.listdir('./')
for f in fList:
  if f.startswith('se_jul') and not f.endswith('.bmp'):
    fnew = f.replace('.','_') + '.bmp'
    os.renames(f,fnew)

print "avconv -i 'se_jul.%03d'  out.avi"
print "ffmpeg -r 1 -f image2 -y -i se_jul_%003d.bmp ... se_jul.avi"

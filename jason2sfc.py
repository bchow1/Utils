#
import urllib2
import json
import sys
import unicodedata
from decimal import Decimal

maxDays = {1:31,2:29,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
sfcFile = open('E:\\Scratch\\vecc_2012.sfc','w')

sfcFile.write('SURFACE\n')
sfcFile.write('11\n')
sfcFile.write('ID      YYMMDD  HOUR    LAT     LON     WSPD    DIR     T       P       H       PRATE\n')
sfcFile.write('NONE            HOURS   N       E       M/S     DEG     C       MB      %       mm/hr\n')
sfcFile.write('-999.000\n')

lat = 22.65043068
lon = 88.43845367

'''
tempm	   Temp in C
hum	   Humidity %
wspdm	   WindSpeed kph
wdird	   Wind direction in degrees
pressurem  Pressure in mBar
precipm	   Precipitation in mm
'''


for month in range(1,13):
  
  for day in range(1,maxDays[month]+1):
    
    url = 'file:///E:\Scratch\met\Kol_2012%02d%02d.json'%(month,day)
    f = urllib2.urlopen(url)
    json_string = f.read()
    parsed_json = json.loads(json_string)
    location    = parsed_json['history']['observations']

    prvHr = -1.0
        
    for i in range(len(location)):
      
      yr   = int(location[i]['date']['year'])
      mon  = int(location[i]['date']['mon'])
      mday = int(location[i]['date']['mday'])
      hr   = float(location[i]['date']['hour'])
      mn   = float(location[i]['date']['min'])
      Hour = hr + mn/60.
      print '%02d%02d%02d %8.3f'%(yr,mon,mday,Hour)
      #print location[i]['wspdm']

      #  Wind speed
      try:
        wspd = float(location[i]['wspdm'])
        wspd = max(0.1,wspd*1e3/3600.)  # m/s
      except:
        wspd = -999.00
      if wspd == -9999.000:
        wspd = -999.00

      #  Wind Direction
      try:
        wdir = float(location[i]['wdird'])
      except:
        wdir = -999.00
      if wdir == -9999.000:
        wdir = -999.00

      #  Temperature
      try:
        tmpr = float(location[i]['tempm'])
      except:
        tmpr = -999.00
      if tmpr == -9999.000:
        tmpr = -999.00

      #  Pressure
      try:
        pres = float(location[i]['pressurem'])
      except:
        pres = -999.00
      if pres == -9999.000:
        pres = -999.00
        
      #  Humidity
      try:
        hum = float(location[i]['hum'])
      except:
        hum = -999.00
      if hum == -9999.000:
        hum = -999.00
        
      #  Precipitation
      try:
        prcp = float(location[i]['precipm'])
      except:
        prcp = -999.00      
      if prcp == -9999.000:
        prcp = -999.00
        
      if Hour != prvHr:
        sfcFile.write('VCC  %02d%02d%02d  %8.3f    %12.8f  %12.8f  %10.3f  %10.3f %10.3f %10.3f %10.3f %10.3f\n'%\
                     (yr,mon,mday,Hour,lat,lon,wspd,wdir,tmpr,pres,hum,prcp))
      prvHr = Hour
      
    f.close()

sfcFile.close()

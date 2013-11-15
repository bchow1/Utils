from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as N
from mpl_toolkits.basemap import Basemap
from netcdftime import utime
from datetime import datetime
import os
from numpy import *
import matplotlib.dates as mdates
from numpy import ma as MA

TSFCmeanall=[]
timeall=[]
time_intall=[]

MainFolder=r"E:/GriddedData/T_SFC/1987/"
for (path, dirs, files) in os.walk(MainFolder):
                        for dir in dirs:
                                print dir
                        path=path+'/'
                
                        for ncfile in files:
                                if ncfile[-3:]=='.nc':
                                    ncfile=os.path.join(path,ncfile)
                                    ncfile=Dataset(ncfile, 'r+', 'NETCDF4')
                                    TSFC=ncfile.variables['T_SFC'][0:20]
                                    TIME=ncfile.variables['time'][0:20]
                                    fillvalue=ncfile.variables['T_SFC']._FillValue
                                    TSFC=MA.masked_values(TSFC, fillvalue)
                                    ncfile.close()

                                    for TSFC, TIME in zip((TSFC[:]),(TIME[:])):
                                        cdftime=utime('seconds since 1970-01-01 00:00:00')
                                        ncfiletime=cdftime.num2date(TIME)
                                        timestr=str(ncfiletime)
                                        d = datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S')
                                        date_string = d.strftime('%Y%m%d%H')
                                        time_int=int(date_string)
 
                                        TSFCmean=N.mean(TSFC)

                                        TSFCmeanall.append(TSFCmean)
                                        timeall.append(ncfiletime)
                                        time_intall.append(time_int)

x=timeall
y=TSFCmeanall
x2=time_intall

fig, ax=plt.subplots(1)

z=N.polyfit(x2,y,1)
p=N.poly1d(z)

plt.plot(x,y)
plt.plot(x,p(x2),'r--') #add trendline to plot

fig.autofmt_xdate()
ax.fmt_xdata=mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
plt.ylabel("Temperature C")
plt.title("Mean Daily Temp")
plt.show()
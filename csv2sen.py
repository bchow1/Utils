import os
import sys
import numpy as np

os.chdir()
dType = {'names':colNames,'formats':colFmt}
print dType

csvFile = 'aztec_20050908_some.csv'
cncDat = np.genfromtxt(csvFile,skiprows=1,delimiter=',',dtype=dType, usemask=True)

#np.genfromtxt(fname, dtype, comments, delimiter, skiprows, skip_header, skip_footer, 
#              converters, missing, missing_values, filling_values, usecols, names, 
#              excludelist, deletechars, replace_space, autostrip, case_sensitive, 
#              defaultfmt, unpack, usemask, loose, invalid_raise)

cncDat['lon'] = cncDat['lon']*-1.
print cncDat['lon'].min(),cncDat['lat'].min()
print cncDat['lon'].max(),cncDat['lat'].max()
print len(cncDat['lon'])
#
import pandas as pd

cName = 'NO_backup/grib2_data/wnd10m.gdas.200601.csv'
print cName
wind = pd.read_csv(cName,names=['ts','te','vName','rmk','lon','lat','vel'])

vel = wind[wind['vName'] == 'UGRD']
vel.rename(columns = {'vel':'uvel'},inplace=True)
#print wind[wind['vName'] == 'VGRD']['vel'].values

vel['vvel'] =  wind[wind['vName'] == 'VGRD']['vel'].values

#print vel.columns
#print vel['uvel'],vel['vvel']

print vel['ts'].values[0]
print vel[vel['ts'] != vel['ts'].values[0]].head(1).index[0]

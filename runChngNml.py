import sys
sys.path.append('/home/user/bnc/python')
import setSCIparams as SCI
mySCIpatt = SCI.Pattern()
#KeyNml={'run_mode':'140'}
#SCI.chngNml('RevCase044_10','RevCase044_10',KeyNml,mySCIpatt.pattNameList,'\n')

KeyNml={'t_avg':'0.0','metfile':'../olad.latlon_utc_stbly.sfc;../olad.latlon_utc.prf'}
SCI.chngNml('x','x',KeyNml,mySCIpatt.pattNameList,'\n')
  

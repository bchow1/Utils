import sqlite3
import utilDb

trlConn = sqlite3.connect('Trial11_conc.db')
trlConn.row_factory = sqlite3.Row
trlCur = trlConn.cursor()

ySmp = utilDb.db2Array(trlCur,'SELECT xd from probdose group by dNo order by dNo',dim=1)
print ySmp

trlConn.close()

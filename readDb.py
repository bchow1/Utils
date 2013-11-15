import sqlite3
import utilDb

trlConn = sqlite3.connect('t05.smp.db')
trlConn.row_factory = sqlite3.Row
trlCur = trlConn.cursor()

ySmp = utilDb.db2Array(trlCur,'SELECT smpID from samTable',dim=1)
print ySmp

trlConn.close()

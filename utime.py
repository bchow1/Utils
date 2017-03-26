import time
import datetime

dt = datetime.datetime.strptime('20160224122738','%Y%m%d%H%M%S')
print time.mktime(dt.timetuple())

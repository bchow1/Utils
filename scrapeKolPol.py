import re
import sys
from urllib import urlopen
from bs4 import BeautifulSoup as bso

#html = urlopen("http://emis.wbpcb.gov.in/airquality/viewautodtldata.do?stn_code=st85&dtl_dt=01/01/2012&param_code=A02")
#html = urlopen("file:///C:/Users/rabin/Google%20Drive/Bapi/IISWBM/Runs/WBPCB_20120101_Rabindrabharati.htm")
html = urlopen("file:///C:/Users/sid/Downloads/WBPCB_20120101_Rabindrabharati.htm")

bsObj = bso(html.read(),"html.parser")
table1 = bsObj.findAll('table')[0]
table2 = bsObj.findAll('table')[1]
table3 = bsObj.findAll('table')[2]
table4 = bsObj.findAll('table')[3]

headers = []
for tr in table3.find_all('tr')[1:]:
  tds = tr.find_all('td')
  headers.append([elem.text.encode('utf-8').replace('\xa0','').replace('\xc2','') for elem in tds])
print headers

records = []
for tr in table4.find_all('tr')[1:]:
  tds = tr.find_all('td')
  records.append([elem.text.encode('utf-8') for elem in tds])
print records
from pyh import *

## Variables ##
myTitle = 'Regression Test'
myRunDate = '10th Oct 2014'
myTable = "Test"

page = PyH(myTitle)
page.addCSS('myStylesheet1.css')
page.addJS('myJavascript1.js', 'myJavascript2.js')
page << div(cl='myCSSclass1 myCSSclass2', id='myDiv1') << p(myRunDate, id='myP1')
page << table()
page << tr('val1' , 'val2' , cl='tr')
page << h1('Details', cl='center')
page << div(cl='myCSSclass1 myCSSclass2', id='myDiv1') << p(myTable, id='myP1')
mydiv2 = page << div(id='myDiv2')
mydiv2 << h2('A smaller title') + p('Followed by a paragraph.')
page << div(id='myDiv3')
page.myDiv3.attributes['cl'] = 'myCSSclass3'
page.myDiv3 << p('Another paragraph')
page.printOut()
page.printOut(file='C:/Users/Bishusunita/BNC/Validation/Test.html')
print 'Done :-)'
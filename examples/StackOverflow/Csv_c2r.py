import csv
x = []
y = []
with (open('E:\\TEMP\\xy.csv','r')) as egFile:
    plots=csv.reader(egFile,delimiter=',')
    for row in plots:
      x.append(int(row[0]))
      y.append(int(row[1]))
print x
print y

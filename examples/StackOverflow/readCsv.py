import csv
data = [] #Buffer list 
with open(r'E:\\TEMP\\tst.csv', "rb") as the_file:
    reader = csv.reader(the_file, delimiter=",")
    for row in reader:

        try:
            new_row = [row[0], row[1], row[2]]
            #Basically write the rows to a list
            data.append(new_row)
        except IndexError as e:
            print e
            pass

    with open("E:\\TEMP\\out.csv", "w+") as to_file:
        writer = csv.writer(to_file, delimiter=",")
        for new_row in data:
            writer.writerow(new_row)
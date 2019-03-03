import csv
with open('airports.csv','r'), open ('abx.csv','w') as fin, fout:
    writer = csv.writer(fout, delimiter=',')            
    for row in csv.reader(fin, delimiter=','):
        if row[3] == 'India':
             writer.writerow(row)
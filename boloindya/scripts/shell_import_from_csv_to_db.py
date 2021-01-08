import csv
from django.db import connections
from random import Random

rand = Random()
cursor = connections['default'].cursor()

csvfile = open('prod_eventbooking.csv', 'rb')
data_list = csv.reader(csvfile, delimiter=',', quotechar='|')
data_list = list(data_list)
columns = data_list.pop(0)

# data_list = data_list[:10]
for row in data_list:
    for row in data_list:
        row[8] = rand.randint(1,5)

query = "INSERT INTO booking_eventbooking (%s) VALUES %s"%(','.join(columns), ','.join(map(str, map(tuple, data_list))))
# print query
query = query.replace("'NULL'", 'null')

cursor.execute(query)

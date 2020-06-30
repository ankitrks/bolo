from forum.user.models import DUser
from django.conf import settings
import csv

def run():
    with open(settings.PROJECT_PATH+'/Compiled Data_IIMJOBS.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                print row
                line_count += 1
                gender = '1' if row[3]=='Male' else '2'
                DUser.objects.create(name =row[0],gender=gender)

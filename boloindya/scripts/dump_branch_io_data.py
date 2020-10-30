import os
import sys
import requests
from datetime import datetime, timedelta

from multiprocessing import Process, Pool

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

from django.conf import settings

branch_io = settings.BRANCH_IO_CONFIG

def run_command(cmd):
    os.system(cmd)

def run_command_in_parallel(command_list):
    if not command_list:
        return 
    pool = Pool(processes=len(command_list))
    for cmd in command_list:
        pool.apply_async(run_command, args=(cmd,))

    pool.close()
    pool.join()

def create_dirs(date, dir_list):
    run_command(" && ".join(["mkdir -p /tmp/%s/%s"%(date, d) for d in dir_list]))

def create_file_commands(date, api_data):
    command_list = []
    file_path_list = []
    for key, link_list in api_data.iteritems():
        for link in link_list:
            file_path = '/tmp/%s/%s/%s'%(date, key, link.split("?")[0].split("/")[-1])
            command_list.append('wget "%s" -O %s'%(link, file_path))
            file_path_list.append(file_path)
    return command_list, file_path_list


def create_aws_upload_command(files):
    return ['aws s3 cp %s s3://%s'%(f, branch_io.get('s3-bucket') + f.replace('/tmp', '', 1)) for f in files]

def get_data(date):
    return requests.post("https://api2.branch.io/v3/export/", json={
        "branch_key": branch_io.get('branch_key'), 
        "branch_secret": branch_io.get('branch_secret'), 
        "export_date": date
    }).json()

def dump_data(date):
    api_data = get_data(date)
    create_dirs(date, api_data.keys())
    download_command_list, file_path_list = create_file_commands(date, api_data)
    run_command_in_parallel(download_command_list)
    run_command_in_parallel(create_aws_upload_command(file_path_list))
    run_command('rm -rf /tmp/%s'%date)
    print "Data dumped for %s"%date

def run(*args):
    if 'runall' in args:
        start_date = datetime.strptime('2020-10-20', '%Y-%m-%d')
    else:
        start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now() - timedelta(days=1)

    while start_date <= end_date:
        print "running for date", start_date.date()
        dump_data(str(start_date.date()))
        start_date += timedelta(days=1)
    
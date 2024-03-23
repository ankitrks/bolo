# this code extracts data from the anroid ngnix logs and will dump them into the models

import re
import ast
import datetime
import pickle
import os

# method for parsing logs and printing the data in form of dict
def parse_logs(filename, counter):
	log_obj_list = []
	current_line = 1
	lineformat = re.compile(r"""(?P<ipaddress>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<dateandtime>\d{2}\/[a-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4})\] ((\"(GET|POST) )(?P<url>.+)( http\/1\.1")) (?P<statuscode>\d{3}) (?P<bytessent>\d+) (["](?P<refferer>(\-)|(.+))["]) (["](?P<useragent>.+)["])""", re.IGNORECASE)
	with open(filename) as lines:
		for line in lines:
			if(current_line >=counter):
				data = re.search(lineformat, line)
				if(data):
					datadict = data.groupdict()
					ip = datadict["ipaddress"]
					dateandtime = datadict["dateandtime"]
					url = datadict["url"]
					referer = datadict["refferer"]
					bytessent = datadict["bytessent"]
					useragent = datadict["useragent"]
					status = datadict["statuscode"]
					method = data.group(6)
					request = data.group(8)
					log_obj_list.append(datadict)

				lastrecord = dateandtime.split(' ')[0]
				obj = dateandtime.strptime(lastrecord,"%d/%b/%Y:%H:%M:%S")
			current_line+=1		
					
	print(len(log_obj_list))															# final number of objects in the list
	return current_line																	# return the marker to the number of objects read in the current file


if __name == '__main__':																# current date-timeobjects 
	now = datetime.now()
	fname_acess_log0 = os.getcwd() + '/access0.log'
	fname_acess_log1 = os.getcwd() + '/access1.log'
	timestamp_log0 = os.path.getmtime(fname_acess_log0)
	dt_timestamp_log0 = datetime.fromtimestamp(timestamp_log0)							#time when the file was last modified

	
	if(os.exists('datetime_record.txt') == False):										# check if the datetime file exists
		datetimeobj = datetime.now()
	else:	
		with open('datetime_record.txt', 'r') as f:
			str_val = f.readlines()
		datetimeobj = datetime.strptime(str_val[0].rstip(), '%Y-%m-%d %H:%M:%S.%f')			# read the datetimeobj from the file, the last time it was read
		print("script last ran on:" datetimeobj)

	if(os.exists('counter.txt') == False):						# check if the file exists if not then assign default value of counter
		counter = 1
	else:	
		with open('counter.txt', 'r') as f:
			counter_val = f.readlines()
		counter = (int)(counter_val[0].rstrip())				 # read the value of counter from the storage
		print("counter value read from file:", counter)

	if(datetimeobj < dt_timestamp_log0):
		print("going in case -1")
		if(os.path.exists(fname_acess_log1)):				#read the complete file acess_log1 starting from index1
			parse_logs(fname_acess_log1, 1)					# reset the counter

		if(os.path.exists(fname_acess_log0)):
			curr_counter = parse_logs(fname_acess_log0, counter)
	else:
		print("going in case-2")
		if(os.path.exists(fname_acess_log0)):
			curr_counter = parse_logs(fname_acess_log0, counter)
			with open('counter.txt', 'w') as f:
				f.write(str(curr_counter) + "\n")

	with open('datetime_record.txt', 'w') as f:			#record the current date-time details to a file
		f.write(str(now) + "\n")		



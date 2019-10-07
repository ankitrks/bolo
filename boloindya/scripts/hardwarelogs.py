# this python script logs the hardware data corrospnoding to the user id's 

from drf_spirit.models import UserJarvisDump, HardwareData
import re 
import time
import pytz
from rest_framework import status 
import ast 
from datetime import datetime 
import os 
local_tz = pytz.timezone("Asia/Kolkata")
import dateutil.parser

#! /usr/bin/python
import sys
import django
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )


# method for parsing records of the hardware logs
def parse_hardware_logs(hardware_log):
	#print(type(hardware_log))
	for key, logs in hardware_log.items():
		userid = key 
		log_str = logs 
		# list containing the list of values to fetch data from
		hardware_mem_req = ["MemTotal", "MemFree", "MemAvailable", "SwapCached", "Active", "Inactive", "Unevictable", "Mlocked", "SwapTotal", "SwapFree", "Dirty" 
		, "Writeback", "AnonPages", "Mapped", "Shmem", "Slab", "SReclaimable", "SUnreclaim", "KernelStack", "PageTables", "NFS_Unstable", "Bounce", "WritebackTmp", "CommitLimit"
		, "Committed_AS", "VmallocTotal", "VmallocUsed", "VmallocChunk"]

		value_list = []
		for item in hardware_mem_req:
			regex_str = r"(?<=" + str(item) +":).{8,22}"			# regex string for parsing the requireed items
			#print(regex_str)
			try:
				matches = re.search(regex_str, log_str).group(0)
				#print(item, matches)
				matches = matches.strip()
				matches = matches.strip('kB')
				value_list.append(matches)

			except Exception as e:
				#print(item, "0")
				value_list.append(0)
				#print(e)

		
		#print(len(value_list))		
		user_hardware_obj = HardwareData(user_id = userid, total_memory = value_list[0], memory_free = value_list[1], memory_available = value_list[2], swap_cached = value_list[3],
			active = value_list[4], inactive = value_list[5], unevictable = value_list[6], locked = value_list[7], swap_total = value_list[8], swap_free = value_list[9],
			dirty = value_list[10], write_back = value_list[11], annon_pages = value_list[12], mapped = value_list[13], shmem = value_list[14], slab = value_list[15],
			sreclaimable = value_list[16], sunreclaimable = value_list[17], kernelstack = value_list[18], pagetables = value_list[19], nfs_unstable = value_list[20],
			bounce = value_list[21], writebacktemp = value_list[22], commit_limit = value_list[23], commit_as = value_list[24], malloc_total = value_list[25],
			malloc_used = value_list[26], malloc_chunk = value_list[27])

		user_hardware_obj.save()		



def main():

	all_hardware_logs = UserJarvisDump.objects.filter(is_executed = False, dump_type = 3)
	for each_log in all_hardware_logs:
		each_hardware_log = each_log.dump 
		hardware_log_string = ast.literal_eval(each_hardware_log) 
		parse_hardware_logs(hardware_log_string)
		unique_id = each_log.pk 
		UserJarvisDump.objects.filter(pk = unique_id).update(is_executed = True, dump_type = 3)


def run():
	main()

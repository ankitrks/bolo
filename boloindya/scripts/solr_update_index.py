import os

def run():
	command = '/var/live_code/boloindya/pyenv/bin/python' + ' ' +'/var/live_code/boloindya/boloindya/manage_local.py runscript'+' '+'update_index -v2'
	command_response = os.system(command)
	print command_response
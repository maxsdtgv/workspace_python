import serial
import time
import datetime
import sys
import string
import os
import subprocess
import threading
import Queue
import signal
import pathlib


'''
def exec_command(command):
	ON_POSIX = 'posix' in sys.builtin_module_names
	command = '"' + command.replace(' ', '","') + '"'

	temp_proc = subprocess.Popen(["ll"], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX, shell=False)
	temp_out = temp_proc.communication()[0]
	if temp_proc.poll() == None:
		temp_proc.terminate()		
	return temp_out

text = exec_command('netstat -nlp')
print text

ON_POSIX = 'posix' in sys.builtin_module_names
temp_proc1 = subprocess.Popen(["ls"], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX, shell=False)
temp_out = temp_proc1.communicate()[0]
if temp_proc1.poll() == None:
	temp_proc1.terminate()		
print temp_out
'''

def exec_command(command):
	ON_POSIX = 'posix' in sys.builtin_module_names

	tmp_command = "'" + command.replace(" ", "' '") + "'"
	print ('commanddd=' + tmp_command)

	temp_proc = subprocess.Popen([tmp_command], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX, shell=True)
	temp_out = temp_proc.communicate()[0]

	if temp_proc.poll() == None:
		temp_proc.terminate()		
	return temp_out

print(exec_command('netstat -nlp'))
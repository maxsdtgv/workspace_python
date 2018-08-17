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

def exec_command(command):
	ON_POSIX = 'posix' in sys.builtin_module_names

	command = '"' + command.replace(' ', '","') + '"'

	print('commandg ====' + command)

	temp_proc = subprocess.Popen(["netstat","-nlp"], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX, shell=False)
	print (temp_proc.communicate())[0]
	
	if temp_proc.poll() == None:
		temp_proc.terminate()		
	
	return

print (exec_command('netstat -nlp | grep openssl'))


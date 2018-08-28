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
import shlex

def queue_output(out, nqueue):
	for line in iter(out.readline, b''):
		nqueue.put(line)
	out.close()

proto = 0 # tls=0, dtls =1

logs = 1

test_iter = 100 # number of tests

test_ipv4v6 = 1 # ipv4=0, ipv6 =1
key_file_name = "rootCA.key"
pem_file_name = "rootCA.pem"
ON_POSIX = 'posix' in sys.builtin_module_names


print('=================== Threads for openssl listeners')
ON_POSIX = 'posix' in sys.builtin_module_names

arr_proc = []
arr_threads = []
arr_queue = []


print('\r\n')		
print('=================== Threads for openssl listeners')
ON_POSIX = 'posix' in sys.builtin_module_names
for i in range(1, 7):
	print('iteration start'+str(i))
	if proto == 0:         # for tls
		temp_str = 'openssl s_server -accept 556' + str(i) + ' -key ' + key_file_name + ' -cert ' + pem_file_name
		if test_ipv4v6 == 1:
			temp_str += ' -6'
			print ('     Starting for TLS openssl server on port 556' + str(i))

	if proto == 1:         # for dtls
		temp_str = 'openssl s_server -psk AABC3BDFDE2526E815D76A22A364BA76641D3360A4A5FBEA9db8bed55d406982 -nocert -dtls -accept 557' + str(i)
		if test_ipv4v6 == 1:
			temp_str += ' -6'
			print ('     Starting for DTLS openssl server on port 557' + str(i))

	arr_proc.append(subprocess.Popen(shlex.split(temp_str), stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX))
	arr_queue.append(Queue.Queue())
	arr_threads.append(threading.Thread(target=queue_output, args=(arr_proc[i-1].stdout, arr_queue[i-1])))
	arr_threads[i-1].daemon = True # thread dies with the program
	arr_threads[i-1].start()
	print('iteration stop'+str(i))
super_print('============================================')
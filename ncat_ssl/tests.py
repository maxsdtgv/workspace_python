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


def ssl_open_server(proto):

		#====================================================================================================================
		#	Threads for openssl listeners
		#====================================================================================================================
		print('=================== Threads for openssl listeners')
		ON_POSIX = 'posix' in sys.builtin_module_names
		global proc1
		global proc2
		global proc3
		global proc4
		global proc5
		global proc6
		global proc7
		if proto == 0:         # for tls
			proc1 = subprocess.Popen(["ping", "8.8.8.8"], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
			proc2 = subprocess.Popen(["ping", "8.8.8.8"], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
			proc3 = subprocess.Popen(["ping", "8.8.8.8"], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
			proc4 = subprocess.Popen(["ping", "8.8.8.8"], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
			proc5 = subprocess.Popen(["ping", "8.8.8.8"], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
			proc6 = subprocess.Popen(["ping", "8.8.8.8"], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)

		if proto == 1:         # for dtls
			proc1 = subprocess.Popen(["openssl", "s_server", "-psk", "AABC3BDFDE2526E815D76A22A364BA76641D3360A4A5FBEA9db8bed55d406982", "-nocert", "-dtls", "-accept" ,"5571"], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
			proc2 = subprocess.Popen(["openssl", "s_server", "-psk", "AABC3BDFDE2526E815D76A22A364BA76641D3360A4A5FBEA9db8bed55d406982", "-nocert", "-dtls", "-accept" ,"5572"], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
			proc3 = subprocess.Popen(["openssl", "s_server", "-psk", "AABC3BDFDE2526E815D76A22A364BA76641D3360A4A5FBEA9db8bed55d406982", "-nocert", "-dtls", "-accept" ,"5573"], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
			proc4 = subprocess.Popen(["openssl", "s_server", "-psk", "AABC3BDFDE2526E815D76A22A364BA76641D3360A4A5FBEA9db8bed55d406982", "-nocert", "-dtls", "-accept" ,"5574"], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
			proc5 = subprocess.Popen(["openssl", "s_server", "-psk", "AABC3BDFDE2526E815D76A22A364BA76641D3360A4A5FBEA9db8bed55d406982", "-nocert", "-dtls", "-accept" ,"5575"], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
			proc6 = subprocess.Popen(["openssl", "s_server", "-psk", "AABC3BDFDE2526E815D76A22A364BA76641D3360A4A5FBEA9db8bed55d406982", "-nocert", "-dtls", "-accept" ,"5576"], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)

		queue1 = Queue.Queue()
		queue2 = Queue.Queue()
		queue3 = Queue.Queue()
		queue4 = Queue.Queue()
		queue5 = Queue.Queue()
		queue6 = Queue.Queue()


		print('============================================')
		#====================================================================================================================

def ssl_close_server():
	global proc1
	global proc2
	global proc3
	global proc4
	global proc5
	global proc6
	global proc7

	if proc1.poll() == None:
		proc1.terminate()

	if proc2.poll() == None:
		proc2.terminate()

	if proc3.poll() == None:
		proc3.terminate()

	if proc4.poll() == None:
		proc4.terminate()

	if proc5.poll() == None:
		proc5.terminate()

	if proc6.poll() == None:
		proc6.terminate()


ssl_open_server(0)

time.sleep(5)

ssl_close_server()
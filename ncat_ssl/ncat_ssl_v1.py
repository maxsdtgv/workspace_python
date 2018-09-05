#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################
#  NCAT SSL Transparency testing framework  #
#  Maksym Vysochinenko                      #
#  2018-08-14                               #
#  version 1 (ncat_ssl_v1.py)               #
#############################################
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

#====================================================================================================================
#	Configurable parameters
#====================================================================================================================
proto = 1 			# define the protocol: 0 = tls, 1 = dtls
logs = 1			# write logs to files: 1 = enable, 0 = disable 
test_iter = 4 		# number of iterations for each test_case
test_ipv4v6 = 0 	# addressing scheme: 0 = IPv4, 1 = IPv6
ssl_server_log = 1	# enable logging for all ssl servers

uart0_enable = 1					# enable uart0 channel
uart0_log = 1						# frite logs to file for uart0 channel
uart0_at = "/dev/ttyXRUSB0"			# section for AT0 channel configuration
uart0_at_speed = 921600

uart1_enable = 1					# enable uart1 channel
uart1_log = 1						# frite logs to file for uart1 channel
uart1_at = "/dev/ttyXRUSB1"			# section for AT1 channel configuration
uart1_at_speed = 921600

uart2_enable = 1					# enable uart2 channel
uart2_log = 1						# frite logs to file for uart2 channel
uart2_console = "/dev/ttyXRUSB2"	# section for CONSOLE channel configuration
uart2_console_speed = 115200

key_file_name = "rootCA.key"		# define name of the KEY file
pem_file_name = "rootCA.pem"		# define name of the CERTIFICATE file

ssl_server_ipv4 = "172.17.57.243"								# local IPv4 address to bind openssl server
ssl_server_ipv6 = "2001:67c:2e5c:2033:286d:f102:48e1:7abf"		# local IPv6 address to bind openssl server

#====================================================================================================================

#====================================================================================================================
#	System variables
#====================================================================================================================
ssl_server = ''
r = '\r'
n = '\n'

send_str = 'sdff sdf sf s df sd f sdsdfdsfsdf034950 tesg92u94t394'+n

comm_0 = 'AT' + r
comm_1 = '' + r
comm_2 = 'ATE' + r
comm_3 = 'AT+CPSMS=1,,,"10100101","00000000"' + r
comm_4 = 'cbe"setextwake b=0x400 m=0x3FFF"' + r
comm_5 = 'AT+SQNSNVW="certificate",0,'
comm_6 = 'AT+SQNSPCFG=1,2,"",1,0,,,""' + r
comm_7 = 'cbe"cat /fs/sqn/etc/sqn_certs/0.crt"' + r
comm_8 = 'AT+SQNSPCFG=1,2,"0x8C;0x8D;0xAE;0xAF",,,,,"AABC3BDFDE2526E815D76A22A364BA76641D3360A4A5FBEA9db8bed55d406982","Client_identity"' + r
comm_9 = 'AT+SQNSS' + r
comm_10 = '' + r
comm_11 = 'AT+SQNSI' + r
comm_12 = 'AT!="netstat"' + r
comm_13 = 'AT^RESET' + r
comm_14 = 'AT!="infoall"' + r
comm_15 = 'cbe"printlog 1 1"' + r
comm_16 = 'cbe"setlog ncat finest"' + r
comm_17 = 'AT!="showver"' + r
comm_18 = 'AT+SQNSSEND='
comm_19 = 'AT!="ee:stat"' + r
comm_20 = 'AT!="fsm"' + r

line_to_send_console = ''
line_to_send_at0 = ''
line_to_send_at1 = ''
recv_str = ''
close_uarts = 0
arr_proc = []
arr_threads = []
arr_threads_log = []
arr_threads_queue = []
#====================================================================================================================

def timest():
	ts = time.time()
	#st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	return st

def from_UE(ti, ts, tchannel, tprintout, check_response):
	global queue_at0
	global queue_at1
	global queue_console	
	global uart0_enable
	global uart1_enable
	global uart2_enable

	matchFound = 0
	lineslist = []
	for tu in range(0, ti):
		time.sleep(1)

		if tchannel == 'channel0_at':
			if uart0_enable == 1:
				while not queue_at0.empty():
					lineslist.append(queue_at0.get())
			else:
				super_print('     AT0 port is disabled.')

		if tchannel == 'channel1_at':
			if uart1_enable == 1:
				while not queue_at1.empty():
					lineslist.append(queue_at1.get())
			else:
				super_print('     AT1 port is disabled.')

		if tchannel == 'channel2_console':
			if uart2_enable == 1:
				while not queue_console.empty():
					lineslist.append(queue_console.get())
			else:
				super_print('     CONSOLE port is disabled.')

		for line in lineslist:
			line = line.decode().replace('\r', '').replace('\n', '')
			if tprintout == 1:
				super_print(line)
			if line != '' and ts != '':
				if line.find(ts) != -1:
					matchFound = 1
					break
		del lineslist [:]
		if matchFound == 1:
			break
	if check_response == 1 and matchFound == 0:
		super_print('Expected response '+ ts + ' NOT FOUND!!!')
		sys.exit()
	return matchFound

def to_UE(channel, sty):
	global line_to_send_at0	
	global line_to_send_at1	
	global line_to_send_console
	global uart0_enable
	global uart1_enable
	global uart2_enable

	if channel == 'channel0_at':
		if uart0_enable == 1:			
			line_to_send_at0 = sty
		else:
			super_print('     Cant send command = '+ str(sty)+'. AT0 is disabled.')

	if channel == 'channel1_at':
		if uart1_enable == 1:
			line_to_send_at1 = sty
		else:
			super_print('     Cant send command = '+ str(sty)+'. AT1 is disabled.')

	if channel == 'channel2_console':
		if uart2_enable == 1:
			line_to_send_console = sty
		else:
			super_print('     Cant send command = '+ str(sty)+'. CONSOLE is disabled.')

	return

def gotoPSPM(waitPSPM):
	super_print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	super_print('========================== goto PSPM =================================')
	if uart0_enable == 1:
		super_print('     AT0 port rts = ' + str(channel0_at.rts) + ', will set False')
		channel0_at.rts = False
	else:
		super_print('     AT0 port is disabled.')

	if uart1_enable == 1:
		super_print('     AT1 port rts = ' + str(channel1_at.rts) + ', will set False')
		channel1_at.rts = False
	else:
		super_print('     AT1 port is disabled.')

	if uart2_enable == 1:
		super_print('     Console port rts = ' +str(channel2_console.rts))
	else:
		super_print('     CONSOLE port is disabled.')
	

	super_print('     Waiting for PSPM ...')
	if from_UE(waitPSPM, 'eem: Suspending...', 'channel2_console', 0, 1)	 == 1:
		super_print('     UE in PSPM mode! (eem: Suspending...)')			
	else:
		super_print('!    Error. "eem: Suspending..." not found')
		sys.exit()		

def wakeupPSPM(waitPSPM):
	super_print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')		
	super_print('========================== Resume from PSPM ===========================')
	if uart0_enable == 1:
		super_print('     AT0 port rts = ' + str(channel0_at.rts) + ', will set True')
		channel0_at.rts = True
	else:
		super_print('     AT0 port is disabled.')

	if uart1_enable == 1:
		super_print('     AT1 port rts = ' + str(channel1_at.rts) + ', will set True')
		channel1_at.rts = True
	else:
		super_print('     AT1 port is disabled.')

	if uart2_enable == 1:
		super_print('     Console port rts = ' +str(channel2_console.rts))
	else:
		super_print('     CONSOLE port is disabled.')


	super_print('     Resuming from PSPM ...')
	if from_UE(waitPSPM, 'eem: Resuming...', 'channel2_console', 0, 1)	 == 1:
		super_print('     UE in PSO state! (eem: Resuming...)')
	else:
		super_print('!    Error. "eem: Resuming..." not found')
		sys.exit()

def channelDetection():
	super_print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	super_print('======================= Detecting channels ==============================')
	time.sleep(9)
	to_UE('channel0_at',comm_2)  # ============== send ATE
	from_UE(5, '', 'channel0_at', 0, 0)

	to_UE('channel0_at',comm_0)  # ============== send AT
	if from_UE(5, 'OK', 'channel0_at', 0, 1) == 1:
		super_print('     AT channel detected `OK` found')
	else:
		super_print('!    Error. AT channel does not responce')
		sys.exit()

	time.sleep(5)
	to_UE('channel2_console',comm_1)  # ============== send enter
	if from_UE(7, '->', 'channel2_console', 0, 1) == 1:
		super_print('     Console channel detected `->` found')	
	else:
		super_print('!    Error. Console channel does not responce')
		sys.exit()

def queue_channel(out, nqueue):
	global line_to_send_at0
	global line_to_send_at1		
	global line_to_send_console
	global close_uarts
	while True:	#	nqueue.put(line)
		if close_uarts == 1:
			if out == channel0_at:
				if uart0_enable == 1:
					out.close()
					super_print('     AT0 closing ...')
			if out == channel1_at:
				if uart1_enable == 1:
					out.close()
					super_print('     AT1 closing ...')
			if out == channel2_console:
				if uart2_enable == 1:
					out.close()			
					super_print('     CONSOLE closing ...')
			close_uarts = 0
			break
		if out == channel0_at:
			if uart0_enable == 1:
				tmp_line = out.readlines()
				for line in tmp_line:
					nqueue.put_nowait(line.replace('\r','').replace('\n',''))
					if uart0_log == 1:
						log_at0.write('[' + timest() + ']' + ' ' + line)
				if line_to_send_at0 != '':
					#time.sleep(.1)
					#out.write('\r')
					#time.sleep(.1)				
					#out.readlines()
					#time.sleep(.1)
					#while not nqueue.empty():
					#	nqueue.get_nowait()
					out.write(line_to_send_at0)
					line_to_send_at0 = ''

		if out == channel1_at:
			if uart1_enable == 1:
				tmp_line = out.readlines()
				for line in tmp_line:
					nqueue.put_nowait(line.replace('\r','').replace('\n',''))
					if uart0_log == 1:
						log_at1.write('[' + timest() + ']' + ' ' + line)				
				if line_to_send_at1 != '':
					#time.sleep(.1)
					#out.write('\r')
					#time.sleep(.1)				
					#out.readlines()
					#time.sleep(.1)
					#while not nqueue.empty():
					#	nqueue.get_nowait()
					out.write(line_to_send_at1)
					line_to_send__at1 = ''

		if out == channel2_console:
			if uart2_enable == 1:
				tmp_line = out.readlines()
				for line in tmp_line:
					nqueue.put_nowait(line.replace('\r','').replace('\n',''))
					if uart0_log == 1:
						log_console.write('[' + timest() + ']' + ' ' + line)									
				if line_to_send_console != '':
					#time.sleep(.1)				
					#out.readlines()				
					#time.sleep(.1)
					#while not nqueue.empty():
					#	nqueue.get_nowait()
					out.write(line_to_send_console)
					line_to_send_console = ''	

def queue_output(out, ni):
	while True:
		for line in iter(out.readline, b''):
			arr_threads_queue[ni-1].put_nowait(line)
			if ssl_server_log == 1 and line !='':
				arr_threads_log[ni-1].write('[' + timest() + ']' + ' ' + line)
	#out.close()

def clear_queue(nqu):
	while not arr_threads_queue[nqu].empty():
		arr_threads_queue[nqu].get_nowait()

def clear_channel_queue():
	while not queue_at0.empty():
		queue_at0.get_nowait()	
	while not queue_at1.empty():
		queue_at1.get_nowait()
	while not queue_console.empty():
		queue_console.get_nowait()

def ncat_send_data_command_mode(nsocket, data):
	spec_comm = 'AT+SQNSSEND=' + str(nsocket) + r
	to_UE('channel0_at',spec_comm)  
	from_UE(3, '>', 'channel0_at', 1, 1)

	to_UE('channel0_at',data)
	from_UE(2, '', 'channel0_at', 1, 0)

	sys.stdout.write('     Sending CTRL+Z  ...')
	to_UE('channel0_at', '\x1A')
	from_UE(3, 'OK', 'channel0_at', 1, 1)

def ncat_open_sockets(proto):
	#====================================================================================================================
	#	Open NCAT SSL connections
	#====================================================================================================================
		super_print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		super_print('======================= Open NCAT SSL connections ====================')
		if proto == 0:         # for tls
			#for i in range(1,2):         # ============== Open sockets for tls
			for i in range(1,7):         # ============== Open sockets for tls
				spec_comm = 'AT+SQNSD=' + str(i) + ',0,' + str(5560+i) + ',"' + ssl_server + '",0,0,1' + r
				to_UE('channel0_at',spec_comm)  
				from_UE(180, 'OK', 'channel0_at', 1, 1)	
				time.sleep(2)	

		if proto == 1:         # for dtls
			for i in range(1,7):         # ============== Opensockets for dtls
				spec_comm = 'AT+SQNSD=' + str(i) + ',1,' + str(5570+i) + ',"' + ssl_server + '",0,0,1' + r
				to_UE('channel0_at',spec_comm)  
				from_UE(180, 'OK', 'channel0_at', 1, 1)
				time.sleep(2)
	#====================================================================================================================

def ncat_close_sockets():
	#====================================================================================================================
	#	Close NCAT SSL connections
	#====================================================================================================================
		super_print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		super_print('======================= Close NCAT SSL connections')
	       # for tls
		time.sleep(.1)
		for i in range(1,7):         # ============== Open sockets for tls
			spec_comm = 'AT+SQNSH=' + str(i) + r
			to_UE('channel0_at',spec_comm)  
			from_UE(5, 'OK', 'channel0_at', 1, 1)		
			time.sleep(.1)
	#====================================================================================================================

def ncat_info():
	super_print('======================= NCAT info =========================')
	to_UE('channel0_at',comm_9)  # send at+sqnss
	from_UE(5, 'OK', 'channel0_at', 1, 1)	

	to_UE('channel0_at',comm_11)  # send at+sqnsi
	from_UE(5, 'OK', 'channel0_at', 1, 1)

	to_UE('channel0_at',comm_14)  # send cbe"infoall"
	from_UE(5, 'OK', 'channel0_at', 1, 1)

	to_UE('channel0_at',comm_12)  # send cbe"netstat"
	from_UE(5, 'OK', 'channel0_at', 1, 1)

	to_UE('channel0_at',comm_19)  # send 
	from_UE(5, 'OK', 'channel0_at', 1, 1)

	to_UE('channel0_at',comm_20)  # send 
	from_UE(5, 'OK', 'channel0_at', 1, 1)

	super_print('exec => netstat -nlp --inet --inet6')
	super_print(exec_command('netstat -nlp --inet --inet6'))

def ssl_open_server(proto):

	#====================================================================================================================
	#	Threads for openssl listeners
	#====================================================================================================================
	super_print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	super_print('=================== Starting threads for openssl listeners')
	ON_POSIX = 'posix' in sys.builtin_module_names

	del arr_proc [:]
	del arr_threads [:]
	del arr_threads_queue [:]
	for i in range(1,7):

		if proto == 0:         # for tls
			temp_str = 'openssl s_server -accept 556' + str(i) + ' -key ' + key_file_name + ' -cert ' + pem_file_name
			if test_ipv4v6 == 1:
				temp_str += ' -6'
			super_print('     Starting TLS server on port 556' + str(i))
			super_print('            exec = ' + temp_str)

		if proto == 1:         # for dtls
			temp_str = 'openssl s_server -psk AABC3BDFDE2526E815D76A22A364BA76641D3360A4A5FBEA9db8bed55d406982 -nocert -dtls -accept 557' + str(i)
			if test_ipv4v6 == 1:
				temp_str += ' -6'
			super_print ('     Starting DTLS server on port 557' + str(i))
			super_print('            exec = ' + temp_str)
		arr_proc.append(subprocess.Popen(shlex.split(temp_str), stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0, close_fds=ON_POSIX,universal_newlines=True))
		arr_threads_queue.append(Queue.Queue())
		arr_threads.append(threading.Thread(target=queue_output, args=(arr_proc[i-1].stdout, i)))
		arr_threads[i-1].daemon = True # thread dies with the program
		arr_threads[i-1].start()
		arr_threads_log[i-1].write('[' + timest() + '] ' + 'New connection ...' + r)
		arr_threads_log[i-1].write('[' + timest() + '] ' + temp_str + r)

	#====================================================================================================================

def ssl_close_server():
	super_print('\r\n')		
	super_print('=================== Close threads for openssl listeners')
	super_print ('     Closing SSL server')
	for i in range(0,6):
		try:

			if arr_proc[0] and arr_proc[0].poll() == None:
				arr_proc[0].terminate()
				super_print ('     Proc ' + str(i+1) + ' closed.'+' obj='+str(arr_proc[0]))
				arr_proc.pop(0)
			else:
				super_print ('     Cant close, proc ' + str(i+1) + ' for openssl does not exist.')
		except IndexError:
			super_print ('     Exception. Proc ' + str(i+1) + ' IndexError.')		
		time.sleep(.6)

def exec_command(command):
	ON_POSIX = 'posix' in sys.builtin_module_names
	tmp_command = "'" + command.replace(" ", "' '") + "'"
	temp_proc = subprocess.Popen([tmp_command], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX, shell=True)
	temp_out = temp_proc.communicate()[0]

	if temp_proc.poll() == None:
		temp_proc.terminate()		
	return temp_out

def super_print(super_string):
	print(super_string)
	log_terminal.write('[' + timest() + ']' + ' ' + super_string+'\r\n')
	
def test_case_1(proto): # Just open/close NCAT SSL TLS/DTLS sessions in loop
	if proto == 1:          # For DTLS Secure renegotiation not supported in openssl, so reopen needed in each loop
		ssl_open_server(1)
	
	ncat_info()
	ncat_open_sockets(proto)
	ncat_info()

	gotoPSPM(120)

	super_print ('Waiting for 10 seconds...')
	time.sleep(10)

	wakeupPSPM(15)
	time.sleep(5)

	channelDetection()
	
	setlog_ncat_finest()

	ncat_info()
	ncat_close_sockets()
	time.sleep(2)
	
	if proto == 1:          # For DTLS Secure renegotiation not supported in openssl, so reopen needed in each loop
		ssl_close_server()
	time.sleep(2)

def test_case_2(proto): # Sending data between UE and server
	global recv_str
	
	gotoPSPM(120)

	super_print ('Waiting for 10 seconds...')
	time.sleep(10)

	wakeupPSPM(15)
	time.sleep(5)

	channelDetection()
	
	setlog_ncat_finest()

	time.sleep(.5)
	
	# Clear thread queues before received data on server side
	for i in range (1,7):
		clear_queue(i-1)

	clear_channel_queue()

	# Send data through sockets by turn
	for i in range (1,7):
		super_print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		super_print('======================= Sending data to server, UE socket = ' + str(i) +' ...')

		ncat_send_data_command_mode(i, send_str)
		super_print('Sent string size on UE = ' + str(len(send_str)))

		time.sleep(15)
		#super_print('Sending string = ')
		#uuu = ":".join("{:02x}".format(ord(c)) for c in send_str)
		#super_print(str(uuu))

		while not arr_threads_queue[i-1].empty():
			recv_str = arr_threads_queue[i-1].get_nowait()

		#super_print('Received string = ')
		#super_print(recv_str)
		#uuu = ":".join("{:02x}".format(ord(c)) for c in recv_str)
		#super_print(str(uuu))

		super_print('Received string size on server= ' + str(len(recv_str)))

		if send_str == recv_str:
			super_print('Strings are matched.')
		else:
			super_print('Received wrong string on ssl server side!')
			super_print('Sending string = ')
			uuu = ":".join("{:02x}".format(ord(c)) for c in send_str)
			super_print(str(uuu))			
			super_print('Received string = ')
			uuu = ":".join("{:02x}".format(ord(c)) for c in recv_str)
			super_print(str(uuu))			
			sys.exit()
	
		super_print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		super_print('======================= Sending data to UE, server = ' + str(i) +' ...')
		#raw_input("Press Enter to continue...")
		arr_proc[i-1].stdin.write(send_str)
		super_print('Sent string size on server = ' + str(len(send_str)))		
		#================== resume from sleep ============================================
		spec_comm = 'AT!="ping ' + ssl_server + '"' + r
		to_UE('channel0_at',spec_comm)  
		from_UE(10, 'OK', 'channel0_at', 0, 0)
		#=================================================================================
		super_print('Waiting for URC ...')
		from_UE(60, '+SQNSRING: '+str(i), 'channel0_at', 0, 1)
		super_print('+SQNSRING: '+str(i)+' found!')
		
		time.sleep(0.4)
		spec_comm = 'at+sqnsrecv=' + str(i) + ',1500' + r
		to_UE('channel0_at',spec_comm)  
		from_UE(3, 'OK', 'channel0_at', 0, 1)	

		while not queue_at0.empty():
			if queue_at0.get().find('+SQNSRECV') != -1:
				recv_str = queue_at0.get()
		clear_channel_queue()

		super_print('Received string size on UE= ' + str(len(recv_str)))

		if send_str == recv_str:
			super_print('Strings are matched.')
		else:
			super_print('Received wrong string on ssl server side!')
			super_print('Sending string = ')
			uuu = ":".join("{:02x}".format(ord(c)) for c in send_str)
			super_print(str(uuu))			
			super_print('Received string = ')
			uuu = ":".join("{:02x}".format(ord(c)) for c in recv_str)
			super_print(str(uuu))			
			sys.exit()

def setlog_ncat_finest():
	to_UE('channel2_console',comm_15)                    # =====   printlog 1 1
	from_UE(2, '->', 'channel2_console', 0, 1)

	to_UE('channel2_console',comm_16)                       # =====   setlog ncat finest
	from_UE(2, '->', 'channel2_console', 0, 1)

try:

#====================================================================================================================
#	Main configs
#====================================================================================================================
	print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	print('======================= Log files creation ...')

	tst = time.time()
	name_time = datetime.datetime.fromtimestamp(tst).strftime('%Y-%m-%d_%H:%M:%S')
	log_terminal = open(name_time+'_terminal.txt', 'w')
	log_terminal.write('Log from terminal\r\n')
	super_print ('     Log file for terminal is created - ' + name_time + '_terminal.txt')

	if uart0_log == 1:
		log_at0 = open(name_time+'_at0.txt', 'w')
		log_at0.write('Log from AT0\r\n')
		super_print ('     Log file for AT0 is created - ' + name_time+'_at0.txt')

	if uart1_log == 1:
		log_at1 = open(name_time+'_at1.txt', 'w')
		log_at1.write('Log from AT1\r\n')
		super_print ('     Log file for AT1 is created - ' + name_time+'_at1.txt')

	if uart2_log == 1:	
		log_console = open(name_time+'_console.txt', 'w')
		log_console.write('Log from console\r\n')
		super_print ('     Log file for console is created - ' + name_time + '_console.txt')

	if ssl_server_log == 1:
		for i in range(0,6):
			arr_threads_log.append(open(name_time+'_ssl_server_' + str(i+1) + '.txt', 'w'))
			arr_threads_log[i].write('Log from server '+ str(i+1)+'\r\n')
			super_print ('     Log file for ssl server '+ str(i+1) +' is created - ' + name_time + '_ssl_server_'+ str(i+1) +'.txt')


	if test_ipv4v6 == 1:
		ssl_server = ssl_server_ipv6
	else:
		ssl_server = ssl_server_ipv4


	if proto == 0:
		super_print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		super_print('======================= SSL/TLS =============================')	
		super_print('     Will be provided ' + str(test_iter) + ' iterations')
		super_print('     Server address = ' + ssl_server)
	else:
		super_print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		super_print('======================= SSL/DTLS =============================')				
		super_print('     Will be provided ' + str(test_iter) + ' iterations')
		super_print('     Server address = ' + ssl_server)		

#====================================================================================================================

#====================================================================================================================
#	Open uarts
#====================================================================================================================
	super_print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	super_print('======================= Open uarts ...')
	if uart0_enable == 1:
		channel0_at = serial.Serial(uart0_at, uart0_at_speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port
		super_print('     AT0 port = ' + channel0_at.name + ' speed = ' + str(uart0_at_speed) + ' rts = ' + str(channel0_at.rts))
	else:
		channel0_at = None
	
	if uart1_enable == 1:
		channel1_at = serial.Serial(uart1_at, uart1_at_speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port
		super_print('     AT1 port = ' + channel1_at.name + ' speed = ' + str(uart1_at_speed) + ' rts = ' + str(channel1_at.rts))
	else:
		channel1_at = None
	
	if uart2_enable == 1:
		channel2_console = serial.Serial(uart2_console, uart2_console_speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port
		super_print('     Console port = ' + channel2_console.name + ' speed = ' + str(uart2_console_speed) + ' rts = ' +str(channel2_console.rts))
	else:
		channel2_console = None
#====================================================================================================================

#====================================================================================================================
#	Check for key and pem files
#====================================================================================================================

	if proto == 0:
		super_print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		super_print('======================= Check for key and pem files (TLS)')
		file_rootCA_key = pathlib.Path("./" + key_file_name)
		if file_rootCA_key.is_file():
			super_print('     Private key = ' + str(file_rootCA_key) + ' found!')   # file exists
		else:
			super_print('!    Private key = ' + str(file_rootCA_key) + ' NOT found!')
			sys.exit()

		file_rootCA_pem = pathlib.Path("./" + pem_file_name)
		if file_rootCA_pem.is_file():
			super_print('     Cert = ' + str(file_rootCA_pem) + ' found!')   # file exists
		else:
			super_print('!    Cert = ' + str(file_rootCA_pem) + ' NOT found!')
			sys.exit()	
#====================================================================================================================
	
#====================================================================================================================
#	Threads for uart readings
#====================================================================================================================
	super_print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	super_print('=================== Threads for uart readings')
	super_print('     Create threads and queues ...')
	if uart0_enable == 1:
		queue_at0 = Queue.Queue()		
		thread_at0 = threading.Thread(target=queue_channel, args=(channel0_at, queue_at0))
		thread_at0.daemon = True # thread dies with the program
		thread_at0.start()
		super_print('     Threads and queue for AT0 ...')
	if uart1_enable == 1:
		queue_at1 = Queue.Queue()
		thread_at1 = threading.Thread(target=queue_channel, args=(channel1_at, queue_at1))	
		thread_at1.daemon = True # thread dies with the program
		thread_at1.start()
		super_print('     Threads and queue for AT1 ...')		
	if uart2_enable == 1:
		queue_console = Queue.Queue()
		thread_console = threading.Thread(target=queue_channel, args=(channel2_console, queue_console))
		thread_console.daemon = True # thread dies with the program
		thread_console.start()
		super_print('     Threads and queue for CONSOLE ...')			
	super_print('     Done.')
#====================================================================================================================

#====================================================================================================================
#	Resetting the board
#====================================================================================================================
	channelDetection()	

	super_print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	super_print('=================== Resetting the board ...')
	to_UE('channel0_at',comm_13)  # send at^reset
	if from_UE(25, '+SYSSTART', 'channel0_at', 0, 1) == 1:
		super_print('     Expected response +SYSSTART is found!')
	
	channelDetection()
#====================================================================================================================

#====================================================================================================================
#	Check version of the firmware
#====================================================================================================================
	super_print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	super_print('=================== Check version of the firmware ...')
	to_UE('channel0_at',comm_17)  # send at!="showver"
	from_UE(5, 'OK', 'channel0_at', 1, 1)
#====================================================================================================================

#====================================================================================================================
#	AT commands for LPM prepare
#====================================================================================================================

	super_print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	super_print('======================= LPM preparation')
	to_UE('channel0_at',comm_2)  # ============== send ATE
	from_UE(2, 'OK', 'channel0_at', 0, 1)

	to_UE('channel0_at',comm_3)  # ============== send AT+CPSMS=1,,,"10100101","00000000"
	from_UE(2, 'OK', 'channel0_at', 1, 1)

	to_UE('channel2_console',comm_4)  # ============== send cbe"setextwake b=0x800 m=0x3FFF"
	from_UE(2, '->', 'channel2_console', 1, 1)
#====================================================================================================================

#====================================================================================================================
#	AT commands for NCAT SSL prepare
#====================================================================================================================
	#ncat_info()
	if proto == 0:
		super_print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		super_print('======================= NCAT SSL/TLS preparation =====================')

		to_UE('channel0_at',comm_5 + str(os.path.getsize(str(file_rootCA_pem))) + r)  # ============== Upload cert rootCA.pem
		if from_UE(2, '>', 'channel0_at', 1, 1) == 1:
			file_pem = open(str(file_rootCA_pem),'r')
			to_UE('channel0_at',file_pem.read())
			file_pem.close()

			if from_UE(2, 'OK', 'channel0_at', 1, 1) == 1:
				super_print('Cert upload suceed!')
			else:
				super_print('Upload cert fail.')
				sys.exit()
			from_UE(1, '', 'channel2_console', 0, 0)
			to_UE('channel2_console',comm_7)
			from_UE(2, '->', 'channel2_console', 1, 1)	
		else:
			super_print('Upload cert fail. No ">" found.')
			sys.exit()

		to_UE('channel0_at',comm_6)  # ============== Configure SSL/TLS security profile configuration AT+SQNSPCFG=1,2,"",1,0,,,""
		from_UE(3, 'OK', 'channel0_at', 1, 1)
		super_print('============================================')

	if proto == 1:
		super_print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		super_print('======================= NCAT SSL/DTLS preparation ====================')
		to_UE('channel0_at',comm_8)          #AT+SQNSPCFG=1,2,"0x8C;0x8D;0xAE;0xAF",,,,,"AABC3BDFDE2526E815D76A22A364BA76641D3360A4A5FBEA9db8bed55d406982","Client_identity"
		from_UE(5, 'OK', 'channel0_at', 1, 1)
		super_print('============================================')
		#==========================Next the same for TLS and DTLS ========================================

	super_print('=================== Secure Socket Configuration =========================')
	for i in range(1,7):         # ============== Configure Secure Socket Configuration AT+SQNSSCFG=i,1,1
		spec_comm = 'AT+SQNSSCFG=' + str(i) + ',1,1' + r
		to_UE('channel0_at',spec_comm)  
		from_UE(5, 'OK', 'channel0_at', 1, 1)	

	super_print('=================== Socket Configuration =========================')
	for i in range(1,7):         # ============== Configure Secure Socket Configuration AT+SQNSSCFG=i,1,1
		spec_comm = 'AT+SQNSCFG=' + str(i) + ',1,300,0,600,5' + r
		to_UE('channel0_at',spec_comm)  
		from_UE(5, 'OK', 'channel0_at', 1, 1)
	super_print('============================================')
#====================================================================================================================

#====================================================================================================================
#	Tests loop
#====================================================================================================================	
	setlog_ncat_finest()
	if proto == 0:
		ssl_open_server(0)

	# ===================================== Test case 1 ===================================
	super_print('====================================================================')
	super_print('          TEST CASE 1 - CONNECT/DISCONNECT to server in loop')
	super_print('====================================================================')
	for i in range(1, test_iter+1):
		super_print('====================================================================')
		super_print('                      Test case 1, loop = ' + str(i))
		super_print('====================================================================')
		test_case_1(proto)
	super_print('====================================================================')
	super_print('                      Test case 1 ended suceed')
	super_print('====================================================================')	
	#======================================= End test case 1 ==============================


	# ===================================== Test case 2 ===================================
	super_print('====================================================================')
	super_print('          TEST CASE 2 - Data transfer between UE/Server ')
	super_print('====================================================================')
	if proto == 1:
		ssl_open_server(1)

	# Open sockets on UE side
	#ncat_info()
	ncat_open_sockets(proto)
	ncat_info()

	for i in range(1, test_iter+1):
		super_print('====================================================================')
		super_print('                      Test case 2, loop = ' + str(i))
		super_print('====================================================================')
		test_case_2(proto)
		time.sleep(2)

	ncat_info()
	ncat_close_sockets()

	if proto == 1:          # For DTLS Secure renegotiation not supported in openssl, so reopen needed in each loop
		ssl_close_server()
	super_print('====================================================================')
	super_print('                      Test case 2 ended suceed')
	super_print('====================================================================')	
	#======================================= End test case 2 ==============================
	if proto == 0:
		ssl_close_server()

#====================================================================================================================

finally:
	super_print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')	
	super_print('===================== Finalize ============================')
	super_print('         Close uarts ...')
	close_uarts = 1
	time.sleep(.5)
	if uart0_enable == 1 and not channel0_at.isOpen():
		super_print('             AT0 is closed.')
	if uart1_enable == 1 and not channel1_at.isOpen():
		super_print('             AT1 is closed.')
	if uart2_enable == 1 and not channel2_console.isOpen():
		super_print('             CONSOLE is closed.')

	super_print('         Close log files ...')
	if ssl_server_log == 1:
		for i in range (0,6):
			arr_threads_log[i].close()


	ssl_close_server()

	if uart0_log == 1:
		log_at0.close()
	if uart1_log == 1:
		log_at1.close()	
	if uart2_log == 1:
		log_console.close()
	log_terminal.close()	

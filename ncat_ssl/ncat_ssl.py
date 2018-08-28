#!/usr/bin/env python
# -*- coding: utf-8 -*-

############################
#  NCAT SSL Transparency   #
#  Maksym Vysochinenko     #
#  2018-08-14              #
#                          #
############################

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
proto = 0 # tls=0, dtls =1
logs = 1
test_iter = 25 # number of tests
test_ipv4v6 = 1 # ipv4=0, ipv6 =1

uart0_at = "/dev/ttyXRUSB0"
uart0_at_speed = 921600

uart1_at = "/dev/ttyXRUSB1"
uart1_at_speed = 921600

uart2_console = "/dev/ttyXRUSB2"
uart2_console_speed = 115200

key_file_name = "rootCA.key"
pem_file_name = "rootCA.pem"

ssl_server_ipv4 = "172.17.57.243"
ssl_server_ipv6 = "2001:67c:2e5c:2033:a8:b11:79ae:8b0d"
#====================================================================================================================

#====================================================================================================================
#	System variables
#====================================================================================================================
ssl_server = ''
r = '\r'
n = '\n'
comm_0 = 'AT' + r
comm_1 = '' + r
comm_2 = 'ATE' + r
comm_3 = 'AT+CPSMS=1,,,"10100101","00000000"' + r
comm_4 = 'cbe"setextwake b=0x800 m=0x3FFF"' + r
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

proc1 = ''
proc2 = ''
proc3 = ''
proc4 = ''
proc5 = ''
proc6 = ''
proc7 = ''
line_to_send_console = ''
line_to_send_at0 = ''
line_to_send_at1 = ''
close_uarts = 0
arr_proc = []
arr_threads = []
arr_queue = []
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

	matchFound = 0
	lineslist = []
	for tu in range(0, ti):
		time.sleep(1)
		if tchannel == 'channel0_at':
			while not queue_at0.empty():
				lineslist.append(queue_at0.get())

		if tchannel == 'channel1_at':
			while not queue_at1.empty():
				lineslist.append(queue_at1.get())

		if tchannel == 'channel2_console':
			while not queue_console.empty():
				lineslist.append(queue_console.get())

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
		super_print('Expected responce '+ ts + ' NOT FOUND!!!')
		sys.exit()
	return matchFound

def to_UE(channel, sty):
	global line_to_send_at0	
	global line_to_send_at1	
	global line_to_send_console

	if channel == 'channel0_at':
		line_to_send_at0 = sty

	if channel == 'channel1_at':
		line_to_send_at1 = sty

	if channel == 'channel2_console':
		line_to_send_console = sty
	return

def gotoPSPM(waitPSPM):
	super_print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	super_print('========================== goto PSPM =================================')
	super_print('     AT0 port rts = ' + str(channel0_at.rts) + ', will set False')
	super_print('     AT1 port rts = ' + str(channel1_at.rts) + ', will set False')
	super_print('     Console port rts = ' +str(channel2_console.rts))
	channel0_at.rts = False
	channel1_at.rts = False
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
	super_print('     AT0 port rts = ' + str(channel0_at.rts) + ', will set True')
	super_print('     AT1 port rts = ' + str(channel1_at.rts) + ', will set True')
	super_print('     Console port rts = ' +str(channel2_console.rts))
	channel0_at.rts = True
	channel1_at.rts = True
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

	time.sleep(9)
	to_UE('channel2_console',comm_1)  # ============== send enter
	if from_UE(5, '->', 'channel2_console', 0, 1) == 1:
		super_print('     Console channel detected `->` found')	
	else: 
		super_print('!    Error. Console channel does not responce')
		sys.exit()

def queue_channel(out, nqueue):
	global line_to_send_at0
	global line_to_send_at1		
	global line_to_send_console

	while True:	#	nqueue.put(line)
		if close_uarts == 1:
			out.close()
			break
		if out == channel0_at:
			tmp_line = out.readlines()
			for line in tmp_line:
				nqueue.put(line.replace('\r','').replace('\n',''))
				log_at0.write('[' + timest() + ']' + ' ' + line)
			if line_to_send_at0 != '':
				time.sleep(.1)
				out.write('\r')
				time.sleep(.1)				
				out.readlines()
				time.sleep(.1)
				while not nqueue.empty():
					nqueue.get()				
				out.write(line_to_send_at0)
				line_to_send_at0 = ''

		if out == channel1_at:
			tmp_line = out.readlines()
			for line in tmp_line:
				nqueue.put(line.replace('\r','').replace('\n',''))
				log_at1.write('[' + timest() + ']' + ' ' + line)				
			if line_to_send_at1 != '':
				time.sleep(.1)
				out.write('\r')
				time.sleep(.1)				
				out.readlines()
				time.sleep(.1)
				while not nqueue.empty():
					nqueue.get()	
				out.write(line_to_send_at1)
				line_to_send__at1 = ''

		if out == channel2_console:
			tmp_line = out.readlines()
			for line in tmp_line:
				nqueue.put(line.replace('\r','').replace('\n',''))
				log_console.write('[' + timest() + ']' + ' ' + line)									
			if line_to_send_console != '':
				time.sleep(.1)				
				out.readlines()				
				time.sleep(.1)
				while not nqueue.empty():
					nqueue.get()	
				out.write(line_to_send_console)
				line_to_send_console = ''	

def queue_output(out, nqueue):
	for line in iter(out.readline, b''):
		nqueue.put(line)
	out.close()

def ncat_open_sockets(proto):
	#====================================================================================================================
	#	Open NCAT SSL connections
	#====================================================================================================================
		super_print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		super_print('======================= Open NCAT SSL connections ====================')
		if proto == 0:         # for tls
			for i in range(1,7):         # ============== Open sockets for tls
				spec_comm = 'AT+SQNSD=' + str(i) + ',0,' + str(5560+i) + ',"' + ssl_server + '",0,0,1' + r
				to_UE('channel0_at',spec_comm)  
				from_UE(180, 'OK', 'channel0_at', 1, 1)		

		if proto == 1:         # for dtls
			for i in range(1,7):         # ============== Opensockets for dtls
				spec_comm = 'AT+SQNSD=' + str(i) + ',1,' + str(5570+i) + ',"' + ssl_server + '",0,0,1' + r
				to_UE('channel0_at',spec_comm)  
				from_UE(180, 'OK', 'channel0_at', 1, 1)

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

	super_print('exec => netstat -nlp --inet --inet6')
	super_print(exec_command('netstat -nlp --inet --inet6'))

def ssl_open_server(proto):

	#====================================================================================================================
	#	Threads for openssl listeners
	#====================================================================================================================
	super_print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	super_print('=================== Threads for openssl listeners')
	ON_POSIX = 'posix' in sys.builtin_module_names
	for i in range(1,7):

		if proto == 0:         # for tls
			temp_str = 'openssl s_server -accept 556' + str(i) + ' -key ' + key_file_name + ' -cert ' + pem_file_name
			if test_ipv4v6 == 1:
				temp_str += ' -6'
				super_print('     Starting for TLS proto server on port 556' + str(i))
				super_print('            exec = ' + temp_str)

		if proto == 1:         # for dtls
			temp_str = 'openssl s_server -psk AABC3BDFDE2526E815D76A22A364BA76641D3360A4A5FBEA9db8bed55d406982 -nocert -dtls -accept 557' + str(i)
			if test_ipv4v6 == 1:
				temp_str += ' -6'
				super_print ('     Starting for DTLS proto server on port 557' + str(i))
				super_print('            exec = ' + temp_str)
		arr_proc.append(subprocess.Popen(shlex.split(temp_str), stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX))
		arr_queue.append(Queue.Queue())
		arr_threads.append(threading.Thread(target=queue_output, args=(arr_proc[i-1].stdout, arr_queue[i-1])))
		arr_threads[i-1].daemon = True # thread dies with the program
		arr_threads[i-1].start()

	super_print('============================================')
	#====================================================================================================================

def ssl_close_server():
	super_print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	super_print('=================== Threads for openssl listeners')
	super_print ('     Closed SSL server')

	for i in range(1,7):
		try:
			if arr_proc[i-1].poll() == None:
				arr_proc[i-1].terminate()
				del arr_proc[i-1]
		except IndexError:
			super_print ('     Cant close, proc ' + str(i) + ' for openssl does not exist.')
	super_print('============================================')

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

	if proto == 1:          # For DTLS Secure renegotiation not supported in openssl, so reopen needed
		ssl_open_server(1)

	ncat_info()
	ncat_open_sockets(proto)
	ncat_info()

	gotoPSPM(60)
	time.sleep(5)

	wakeupPSPM(10)
	time.sleep(5)

	channelDetection()
	
	to_UE('channel2_console',comm_16)                       # =====   setlog ncat finest
	from_UE(2, '->', 'channel2_console', 0, 1)		
	
	ncat_info()
	ncat_close_sockets()
	ncat_info()

	time.sleep(5)

	if proto == 1:          # For DTLS Secure renegotiation not supported in openssl, so reopen needed
		ssl_close_server()
	time.sleep(3)

try:

#====================================================================================================================
#	Main configs
#====================================================================================================================


	tst = time.time()
	name_time = datetime.datetime.fromtimestamp(tst).strftime('%Y-%m-%d_%H:%M:%S')
	log_terminal = open(name_time+'_terminal.txt', 'w')
	log_terminal.write('Log from terminal\r\n')
	
	log_console = open(name_time+'_console.txt', 'w')
	log_console.write('Log from console\r\n')

	log_at0 = open(name_time+'_at0.txt', 'w')
	log_at0.write('Log from AT0\r\n')

	log_at1 = open(name_time+'_at1.txt', 'w')
	log_at1.write('Log from AT1\r\n')

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
	super_print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	super_print('======================= Log files creation finished')
	super_print ('     Log file for terminal is created - ' + name_time + '_terminal.txt')
	super_print ('     Log file for AT0 is created - ' + name_time+'_at0.txt')
	super_print ('     Log file for AT1 is created - ' + name_time+'_at1.txt')
	super_print ('     Log file for console is created - ' + name_time + '_console.txt')
#====================================================================================================================

#====================================================================================================================
#	Open uarts
#====================================================================================================================
	super_print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	super_print('======================= Open uarts ...')
	channel0_at = serial.Serial(uart0_at, uart0_at_speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port
	channel1_at = serial.Serial(uart1_at, uart1_at_speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port
	channel2_console = serial.Serial(uart2_console, uart2_console_speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port

	super_print('     AT0 port = ' + channel0_at.name + ' speed = ' + str(uart0_at_speed) + ' rts = ' + str(channel0_at.rts))
	super_print('     AT1 port = ' + channel1_at.name + ' speed = ' + str(uart1_at_speed) + ' rts = ' + str(channel1_at.rts))
	super_print('     Console port = ' + channel2_console.name + ' speed = ' + str(uart2_console_speed) + ' rts = ' +str(channel2_console.rts))
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
	super_print('     Create queue ...')
	queue_console = Queue.Queue()
	queue_at0 = Queue.Queue()
	queue_at1 = Queue.Queue()
	super_print('     Create threads ...')
	thread_at0 = threading.Thread(target=queue_channel, args=(channel0_at, queue_at0))
	thread_at1 = threading.Thread(target=queue_channel, args=(channel1_at, queue_at1))		
	thread_console = threading.Thread(target=queue_channel, args=(channel2_console, queue_console))

	thread_at0.daemon = True # thread dies with the program
	thread_at1.daemon = True # thread dies with the program
	thread_console.daemon = True # thread dies with the program

	super_print('     Start threads ...')
	thread_at0.start()
	thread_at1.start()	
	thread_console.start()	
	super_print('     Done.')
	super_print('============================================')
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
	ncat_info()
	if proto == 0:
		super_print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		super_print('======================= NCAT SSL/TLS preparation =====================')

		to_UE('channel0_at',comm_5 + str(os.path.getsize(str(file_rootCA_pem))+1) + r)  # ============== Upload cert rootCA.pem
		if from_UE(2, '>', 'channel0_at', 1, 1) == 1:
			file_pem = open(str(file_rootCA_pem),'r')
			to_UE('channel0_at',file_pem.read())
			file_pem.close()

			if from_UE(2, 'OK', 'channel0_at', 1, 1) == 1:
				super_print('Cert upload suceed!')
			else:
				super_print('Upload cert fail.')
				sys.exit()

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
#	Main loop
#====================================================================================================================	
	to_UE('channel2_console',comm_15)                    # =====   printlog 1 1
	from_UE(2, '->', 'channel2_console', 0, 1)
	to_UE('channel2_console',comm_16)                       # =====   setlog ncat finest
	from_UE(2, '->', 'channel2_console', 0, 1)
	
	if proto == 0:
		ssl_open_server(0)

	for i in range(1, test_iter+1):
		super_print('====================================================================')
		super_print('                      Test loop = ' + str(i))
		super_print('====================================================================')

		test_case_1(proto)

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
	if not channel0_at.isOpen():
		super_print('             AT0 is closed.')
	if not channel1_at.isOpen():
		super_print('             AT1 is closed.')
	if not channel2_console.isOpen():
		super_print('             CONSOLE is closed.')

	super_print('         Close subpocesses ...')
	ssl_close_server()

	super_print('         Close log files ...')
	log_console.close()
	log_at0.close()
	log_at1.close()	
	log_terminal.close()	

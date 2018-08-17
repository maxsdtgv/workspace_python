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

proto = 1 # tls=0, dtls =1

uart0_at = "/dev/ttyXRUSB0"
uart0_at_speed = 921600

uart1_at = "/dev/ttyXRUSB1"
uart1_at_speed = 921600

uart2_console = "/dev/ttyXRUSB2"
uart2_console_speed = 115200

key_file_name = "rootCA.key"
pem_file_name = "rootCA.pem"

ssl_server = "172.17.57.221"

r = '\r'
n = '\n'
comm_0 = 'AT' + r
comm_1 = '' + r + n
comm_2 = 'ATE' + r
comm_3 = 'AT+CPSMS=1,,,"10100101","00000000"' + r
comm_4 = 'cbe"setextwake b=0x800 m=0x3FFF"' + r
comm_5 = 'AT+SQNSNVW="certificate",0,'
comm_6 = 'AT+SQNSPCFG=1,2,"",1,0,,,""' + r
comm_7 = 'cbe"cat /fs/sqn/etc/sqn_certs/0.crt"' + r
comm_8 = 'AT+SQNSPCFG=1,2,"0x8C;0x8D;0xAE;0xAF",,,,,"AABC3BDFDE2526E815D76A22A364BA76641D3360A4A5FBEA9db8bed55d406982","Client_identity"' + r
comm_9 = 'AT+SQNSS' + r
comm_10 = '' + r


try:
	def timest():
		ts = time.time()
		#st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
		st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
		return st

	def from_UE(ti, ts, tchannel, tprintout, check_response):
		matchFound = 0
		lineslist = ''
		for tu in range(0, ti):
			time.sleep(1)
			if tchannel == 'channel0_at':
				lineslist = channel0_at.readlines()
			if tchannel == 'channel1_at':
				lineslist = channel1_at.readlines()
			if tchannel == 'channel2_console':
				lineslist = channel2_console.readlines()
			for line in lineslist:
				line = line.decode().replace('\r', '').replace('\n', '')
				if tprintout == 1:
					print(line)
				if line != '' and ts != '':
					if line.find(ts) != -1:
						matchFound = 1
						break
			if matchFound == 1:
				break
		if check_response == 1 and matchFound == 0:
			print('Expected responce NOT FOUND!!!')
			sys.exit()
		return matchFound

	def to_UE(channel, sty):
		if channel == 'channel0_at':
			channel0_at.write(comm_1.encode())
			time.sleep(.2)
			channel0_at.readlines()
			time.sleep(.2)
			channel0_at.write(sty.encode())

		if channel == 'channel1_at':
			channel1_at.write(comm_1.encode())
			time.sleep(.2)
			channel1_at.readlines()
			time.sleep(.2)
			channel1_at.write(sty.encode())

		if channel == 'channel2_console':
			channel2_console.write(comm_1)
			time.sleep(.2)
			channel2_console.readlines()
			time.sleep(.2)
			channel2_console.write(sty)
		return

	def gotoPSPM(waitPSPM):
		print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		print('========================== goto PSPM =================================')
		print('     AT0 port rts = ' + str(channel0_at.rts) + ', will set False')
		print('     AT1 port rts = ' + str(channel1_at.rts) + ', will set False')
		print('     Console port rts = ' +str(channel2_console.rts))
		channel0_at.rts = False
		channel1_at.rts = False
		print('     Waiting for PSPM ...')
		if from_UE(waitPSPM, 'eem: Suspending...', 'channel2_console', 0, 1)	 == 1:
			print('     UE in PSPM mode! (eem: Suspending...)')			
		else:
			print('!    Error. "eem: Suspending..." not found')
			sys.exit()		

	def wakeupPSPM(waitPSPM):
		print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')		
		print('========================== Resume from PSPM ===========================')
		print('     AT0 port rts = ' + str(channel0_at.rts) + ', will set True')
		print('     AT1 port rts = ' + str(channel1_at.rts) + ', will set True')
		print('     Console port rts = ' +str(channel2_console.rts))
		channel0_at.rts = True
		channel1_at.rts = True
		print('     Resuming from PSPM ...')
		if from_UE(waitPSPM, 'eem: Resuming...', 'channel2_console', 0, 1)	 == 1:
			print('     UE in PSO state! (eem: Resuming...)')
		else:
			print('!    Error. "eem: Resuming..." not found')
			sys.exit()

	def channelDetection():
		print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		print('======================= Detecting channels ==============================')
		time.sleep(8)
		to_UE('channel0_at',comm_2)  # ============== send ATE
		from_UE(5, '', 'channel0_at', 0, 0)

		to_UE('channel0_at',comm_0)  # ============== send AT
		if from_UE(5, 'OK', 'channel0_at', 0, 1) == 1:
			print('     AT channel detected `OK` found')
		else: 
			print('!    Error. AT channel does not responce')
			sys.exit()

		to_UE('channel2_console',comm_1)  # ============== send enter
		if from_UE(5, '->', 'channel2_console', 0, 1) == 1:
			print('     Console channel detected `->` found')	
		else: 
			print('!    Error. Console channel does not responce')
			sys.exit()

	def queue_output(out, nqueue):
		for line in iter(out.readline, b''):
			nqueue.put(line)
		out.close()

	def ncat_open_sockets(proto):
		#====================================================================================================================
		#	Open NCAT SSL connections
		#====================================================================================================================
			print('\r\n')		
			sys.stdout.write('[' + timest() + '] ')
			print('======================= Open NCAT SSL connections ====================')
			if proto == 0:         # for tls
				for i in range(1,7):         # ============== Open sockets for tls
					spec_comm = 'AT+SQNSD=' + str(i) + ',0,' + str(5560+i) + ',"' + ssl_server + '",0,0,1' + r
					to_UE('channel0_at',spec_comm)  
					from_UE(5, 'OK', 'channel0_at', 1, 1)		

			if proto == 1:         # for dtls
				for i in range(1,7):         # ============== Opensockets for dtls
					spec_comm = 'AT+SQNSD=' + str(i) + ',1,' + str(5570+i) + ',"' + ssl_server + '",0,0,1' + r
					to_UE('channel0_at',spec_comm)  
					from_UE(5, 'OK', 'channel0_at', 1, 1)

			to_UE('channel0_at',comm_9)  # send at+sqnss
			from_UE(5, 'OK', 'channel0_at', 1, 1)

		#====================================================================================================================
	
	def ncat_close_sockets():
		#====================================================================================================================
		#	Close NCAT SSL connections
		#====================================================================================================================
			print('\r\n')		
			sys.stdout.write('[' + timest() + '] ')
			print('======================= Close NCAT SSL connections')
		       # for tls
			to_UE('channel0_at',comm_9)  # send at+sqnss
			from_UE(5, 'OK', 'channel0_at', 1, 1)

			for i in range(1,7):         # ============== Open sockets for tls
				spec_comm = 'AT+SQNSH=' + str(i) + r
				to_UE('channel0_at',spec_comm)  
				from_UE(5, 'OK', 'channel0_at', 1, 1)		

			to_UE('channel0_at',comm_9)  
			from_UE(5, 'OK', 'channel0_at', 1, 1)

		#====================================================================================================================

	def ssl_open_server(proto):

		#====================================================================================================================
		#	Threads for openssl listeners
		#====================================================================================================================
		print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
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
			proc1 = subprocess.Popen(["openssl", "s_server", "-accept", "5561", "-key", key_file_name, "-cert", pem_file_name], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
			proc2 = subprocess.Popen(["openssl", "s_server", "-accept", "5562", "-key", key_file_name, "-cert", pem_file_name], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
			proc3 = subprocess.Popen(["openssl", "s_server", "-accept", "5563", "-key", key_file_name, "-cert", pem_file_name], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
			proc4 = subprocess.Popen(["openssl", "s_server", "-accept", "5564", "-key", key_file_name, "-cert", pem_file_name], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
			proc5 = subprocess.Popen(["openssl", "s_server", "-accept", "5565", "-key", key_file_name, "-cert", pem_file_name], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
			proc6 = subprocess.Popen(["openssl", "s_server", "-accept", "5566", "-key", key_file_name, "-cert", pem_file_name], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)

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

		thread1 = threading.Thread(target=queue_output, args=(proc1.stdout, queue1))
		thread2 = threading.Thread(target=queue_output, args=(proc2.stdout, queue2))	
		thread3 = threading.Thread(target=queue_output, args=(proc3.stdout, queue3))
		thread4 = threading.Thread(target=queue_output, args=(proc4.stdout, queue4))
		thread5 = threading.Thread(target=queue_output, args=(proc5.stdout, queue5))
		thread6 = threading.Thread(target=queue_output, args=(proc6.stdout, queue6))


		thread1.daemon = True # thread dies with the program
		thread2.daemon = True # thread dies with the program	
		thread3.daemon = True # thread dies with the program
		thread4.daemon = True # thread dies with the program
		thread5.daemon = True # thread dies with the program
		thread6.daemon = True # thread dies with the program

		thread1.start()
		thread2.start()
		thread3.start()
		thread4.start()
		thread5.start()
		thread6.start()
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

	def exec_command(command):
		command = '"' + command.replace(' ', '","') + '"'
		ON_POSIX = 'posix' in sys.builtin_module_names
		temp_proc = subprocess.Popen([command], stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
		temp_out = temp_proc.communication()
		if temp_proc.poll() == None:
			temp_proc.terminate()		
		return temp_out

#====================================================================================================================
#	Uarts connection
#====================================================================================================================
	channel0_at = serial.Serial(uart0_at, uart0_at_speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port
	channel1_at = serial.Serial(uart1_at, uart1_at_speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port
	channel2_console = serial.Serial(uart2_console, uart2_console_speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port

	print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	print('======================= Configs')
	print('     AT0 port = ' + channel0_at.name + ' speed = ' + str(uart0_at_speed) + ' rts = ' + str(channel0_at.rts))
	print('     AT1 port = ' + channel1_at.name + ' speed = ' + str(uart1_at_speed) + ' rts = ' + str(channel1_at.rts))
	print('     Console port = ' + channel2_console.name + ' speed = ' + str(uart2_console_speed) + ' rts = ' +str(channel2_console.rts))
#====================================================================================================================

#====================================================================================================================
#	Check for key and pem files
#====================================================================================================================
	if proto == 0:
		file_rootCA_key = pathlib.Path("./" + key_file_name)
		if file_rootCA_key.is_file():
			print('     Private key = ' + str(file_rootCA_key) + ' found!')   # file exists
		else:
			print('!    Private key = ' + str(file_rootCA_key) + ' NOT found!')
			sys.exit()

		file_rootCA_pem = pathlib.Path("./" + pem_file_name)
		if file_rootCA_pem.is_file():
			print('     Cert = ' + str(file_rootCA_pem) + ' found!')   # file exists
		else:
			print('!    Cert = ' + str(file_rootCA_pem) + ' NOT found!')
			sys.exit()	
#====================================================================================================================

	time.sleep(8)
	channelDetection()

#====================================================================================================================
#	AT commands for LPM prepare
#====================================================================================================================

	print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')
	print('======================= LPM preparation')
	to_UE('channel0_at',comm_2)  # ============== send ATE
	from_UE(2, 'OK', 'channel0_at', 0, 1)

	to_UE('channel0_at',comm_3)  # ============== send AT+CPSMS=1,,,"10100101","00000000"
	from_UE(2, 'OK', 'channel0_at', 1, 1)

	to_UE('channel2_console',comm_4)  # ============== send
	from_UE(2, '->', 'channel2_console', 1, 1)
#====================================================================================================================

#====================================================================================================================
#	AT commands for NCAT SSL prepare
#====================================================================================================================
	if proto == 0:
		print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		print('======================= NCAT SSL/TLS preparation =====================')

		to_UE('channel0_at',comm_5 + str(os.path.getsize(str(file_rootCA_pem))+2) + r)  # ============== Upload cert rootCA.pem
		if from_UE(2, '>', 'channel0_at', 1, 1) == 1:
			file_pem = open(str(file_rootCA_pem),'r')
			to_UE('channel0_at',file_pem.read() + n +'\x1A')
			file_pem.close()

			if from_UE(2, 'OK', 'channel0_at', 1, 1) == 1:
				print('Cert upload suceed!')
			else:
				print('Upload cert fail.')
				sys.exit()

			to_UE('channel2_console',comm_7)
			from_UE(2, '->', 'channel2_console', 1, 1)	
		else:
			print('Upload cert fail. No ">" found.')
			sys.exit()

		to_UE('channel0_at',comm_6)  # ============== Configure SSL/TLS security profile configuration AT+SQNSPCFG=1,2,"",1,0,,,""
		from_UE(3, 'OK', 'channel0_at', 1, 1)
		print('============================================')
	if proto == 1:
		print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		print('======================= NCAT SSL/DTLS preparation ====================')
		to_UE('channel0_at',comm_8)
		from_UE(5, 'OK', 'channel0_at', 1, 1)
		print('============================================')
		#==========================Next the same for TLS and DTLS ========================================
		print('=================== Secure Socket Configuration =========================')
	for i in range(1,7):         # ============== Configure Secure Socket Configuration AT+SQNSSCFG=i,1,1
		spec_comm = 'AT+SQNSSCFG=' + str(i) + ',1,1' + r
		to_UE('channel0_at',spec_comm)  
		from_UE(5, 'OK', 'channel0_at', 1, 1)	
	print('============================================')
#====================================================================================================================


	ssl_open_server(proto)

	for i in range(0, 10):
		print('====================================================================')
		print('                      Test loop = ' + str(i))
		print('====================================================================')

		ncat_open_sockets(proto)

		gotoPSPM(30)
		time.sleep(5)

		wakeupPSPM(10)
		time.sleep(5)

		channelDetection()

		ncat_close_sockets()
		time.sleep(5)

		if proto == 1:          # Secure renegotiation not supported in openssl, so reopen needed
			ssl_close_server()
			ssl_open_server(1)

	ssl_close_server()
	time.sleep(3)

	'''
	while True:

		#time.sleep(.5)
		#print('test next')
		print(threading.enumerate())
		#signal.signal(signal.SIGINT, sigint_handler)
		if not queue1.empty():
			print('thread 1 is alive')
			line = queue1.get()
			print(line)

		#print(proc1.returncode)
		if not queue2.empty():
			print('thread 2 is alive')
			line = queue2.get()
			print(line)

		#print(proc2.returncode)
	'''
finally:
	print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')	
	print('===================== Finalize ============================')
	print('         Close uarts ...')
	channel0_at.close()
	channel1_at.close()	
	channel2_console.close()
	print('         Close subpocesses ...')
	ssl_close_server()
	print('         Done.')
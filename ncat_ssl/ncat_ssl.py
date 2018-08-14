
import serial
import time
import datetime
import sys
import string
import os
import subprocess


server_ssh = "192.168.1.1"

uart0_at = "/dev/ttyXRUSB0"
uart0_at_speed = 921600

uart1_at = "/dev/ttyXRUSB1"
uart1_at_speed = 921600

uart2_console = "/dev/ttyXRUSB2"
uart2_console_speed = 115200

try:
	def timest():
		ts = time.time()
		st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
		return st

	def parss(ti, ts, tchannel, tprintout):
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
		return matchFound

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
		if parss(waitPSPM, 'eem: Suspending...', 'channel2_console', 0)	 == 1:
			print('     UE in PSPM mode! (eem: Suspending...)')			
		else:
			print('     Error. "eem: Suspending..." not found')
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
		if parss(waitPSPM, 'eem: Resuming...', 'channel2_console', 0)	 == 1:
			print('     UE in PSO state! (eem: Resuming...)')
		else:
			print('     Error. "eem: Resuming..." not found')
			sys.exit()

	def channelDetection():
		print('\r\n')		
		sys.stdout.write('[' + timest() + '] ')
		print('======================= Detecting channels ==============================')
		time.sleep(4)
		parss(1, '', 'channel0_at', 0)
		parss(1, '', 'channel1_at', 0)
		parss(1, '', 'channel2_console', 0)
		channel0_at.write(comm_0.encode())  # ============== send ATE
		if parss(2, 'OK', 'channel0_at', 0) == 1:
			print('     AT channel detected `OK` found')
		else: 
			print('     Error. AT channel does not responce')
			sys.exit()

		channel2_console.write(comm_1.encode())  # ============== send enter
		if parss(2, '->', 'channel2_console', 0) == 1:
			print('     Console channel detected `->` found')	
		else: 
			print('     Error. Console channel does not responce')
			sys.exit()


	channel0_at = serial.Serial(uart0_at, uart0_at_speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port
	channel1_at = serial.Serial(uart1_at, uart1_at_speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port
	channel2_console = serial.Serial(uart2_console, uart2_console_speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port
	print('\r\n======================= Configs ==============================')
	print('     AT0 port = ' + channel0_at.name + ' speed = ' + str(uart0_at_speed) + ' rts = ' + str(channel0_at.rts))
	print('     AT1 port = ' + channel1_at.name + ' speed = ' + str(uart1_at_speed) + ' rts = ' + str(channel1_at.rts))
	print('     Console port = ' + channel2_console.name + ' speed = ' + str(uart2_console_speed) + ' rts = ' +str(channel2_console.rts))


	r = '\r'
	n = '\n'
	comm_0 = 'AT'
	comm_1 = ''
	comm_2 = 'ATE'
	comm_3 = 'AT+CPSMS=1,,,"10100101","00000000"'
	comm_4 = 'cbe"setextwake b=0x800 m=0x3FFF"'
	comm_5 = ''
	comm_6 = ''
	comm_7 = ''

	comm_0 += r
	comm_1 += r + n
	comm_2 += r
	comm_3 += r
	comm_4 += r
	comm_6 += r
	comm_7 += r
	'''
	channelDetection()

	print('\r\n======================= LPM preparation ==============================')
	channel0_at.write(comm_2.encode())  # ============== send ATE
	parss(1, 'OK', 'channel0_at', 0)
	channel0_at.write(comm_3.encode())  # ============== send
	parss(2, 'OK', 'channel0_at', 1)
	channel2_console.write(comm_4.encode())  # ============== send
	parss(2, '->', 'channel2_console', 1)

	gotoPSPM(20)
	time.sleep(5)

	wakeupPSPM(10)
	time.sleep(5)

	channelDetection()
	'''
	test = subprocess.Popen(["ping","-W","2","-c", "1", "192.168.1.70"], stdout=subprocess.PIPE)
	output = test.communicate()[0]


finally:
	print('\r\n')		
	sys.stdout.write('[' + timest() + '] ')	
	print('===================== Close uarts ============================')
	channel0_at.close()
	channel1_at.close()	
	channel2_console.close()



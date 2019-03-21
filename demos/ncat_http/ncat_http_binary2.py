#====================================================================================================================
#	The script uses for upload picture directly to the server over POST
#====================================================================================================================

import serial
import os
import time
import sys

#====================================================================================================================
#	Configurable parameters
#====================================================================================================================
server_ip = "172.17.57.154"				# http server
server_port = 80						# server port
method = 0 								# define the method: 0 = POST, 1 = PUT
process_script = "processing_script.php"# script on the server
file_to_upload = "a2.jpg"				# local file without path

uart0_at = "/dev/ttyUSB0"				# section for AT0 channel configuration
uart0_at_speed = 921600

r = '\r'
comm_conf = 'AT+SQNHTTPCFG=0,"' + server_ip + '",' + str(server_port) + ',0,"","",0,120,3,1,0' + r
comm_send = ''
comm_recv = 'AT+SQNHTTPRCV=0' + r
#====================================================================================================================

def reading_resp():
	time.sleep(2)
	tmp_line = channel0_at.readlines()
	for line in tmp_line:
		print(line)
	return

def waiting_response(resp):
	print('Waiting for ' + resp + '...')
	found = 0
	maxtimeout = 2
	for timeout in range(0, maxtimeout):
		tmp_line = channel0_at.readlines()
		for line in tmp_line:
			line = line.replace('\r', '').replace('\n', '')
			if line == resp:
				print('... found.')
				found = 1
				return
		time.sleep(1)
	if found == 0:
		print('... not found. Exit.')
		sys.exit()

try:
# Connect to serial port
	channel0_at = serial.Serial(uart0_at, uart0_at_speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port
	time.sleep(.2)
	channel0_at.readlines()
	channel0_at.write(r)
	channel0_at.readlines()

# File size calculation
	file_fd = open(file_to_upload, 'r')
	file_fd.seek(0, os.SEEK_END)
	size = file_fd.tell()
	file_fd.seek(0)

# Define command to open connection
	if method == 0:
		comm_send = 'AT+SQNHTTPSND=0,' + str(method) + ',"/' + process_script + '",' + str(size) + ',"2"' + r
	else:
		comm_send = 'AT+SQNHTTPSND=0,' + str(method) + ',"/' + file_to_upload + '",' + str(size) + ',"2"' + r
	

	print('Sending ATE ')
	channel0_at.write('ATE0'+r)
	reading_resp()

	print('Read previous data ' + comm_recv)
	channel0_at.write(comm_recv)
	reading_resp()

	print('Sending command ' + comm_conf)
	channel0_at.write(comm_conf)
	reading_resp()

	print('Sending command ' + comm_send)
	channel0_at.write(comm_send)

	waiting_response('> ')

	print('Sending data ...')
	for i_byte in range(0, size):
		byte = file_fd.read(1)
		sys.stdout.write(str(i_byte+1)+"\r")
		channel0_at.write(byte)
		time.sleep(.0001)
		#read_byte = channel0_at.read()
		#print("Data="+str(read_byte))
		#Do stuff with byte.
	sys.stdout.write("\r\nTransfer complete.\r\n")

	time.sleep(1)
	waiting_response('OK')

finally:
	print('Exit programm.')
	file_fd.close()
	channel0_at.close()


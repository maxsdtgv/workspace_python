#====================================================================================================================
#	The script uses for save the picture file from streamer and upload to server over POST
#====================================================================================================================


import serial
import os
import time
import sys
import urllib3
import StringIO
from PIL import Image

#====================================================================================================================
#	Configurable parameters
#====================================================================================================================
server_ip = 'ec2-3-17-146-247.us-east-2.compute.amazonaws.com'				# http server
server_port = 33073					# server port
method = 0 						# define the method: 0 = POST, 1 = PUT
process_script = 'processing_script.php'		# script on the server
file_to_upload = '/tmp/pic.jpg'				#local file without path

uart0_at = '/dev/ttyUSB0'				# section for AT0 channel configuration
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
				return found
		time.sleep(1)
	if found == 0:
		print('... not found. Exit.')
		return found

try:
# Connect to serial port
	channel0_at = serial.Serial(uart0_at, uart0_at_speed, timeout=0, parity=serial.PARITY_NONE, rtscts=True)  # open serial port
	time.sleep(.2)
	channel0_at.readlines()
	channel0_at.write(r)
	channel0_at.readlines()

	http = urllib3.PoolManager()

	print('Sending ATE ')
	channel0_at.write('ATE0'+r)
	reading_resp()
	
	print('Read previous data ' + comm_recv)
	channel0_at.write(comm_recv)
	reading_resp()

	print('Sending command ' + comm_conf)
	channel0_at.write(comm_conf)
	reading_resp()
	
	while True:

# Download file from streamer
		print('Download pic file...')
		resp_http = http.request('GET', 'http://127.0.0.1:8080/?action=snapshot')
		myfile = open(file_to_upload, 'w')                                                                                  
	        myfile.write(resp_http.data)                                                                                
		myfile.close()

# Compress the file
		buffer = StringIO.StringIO()
		im1 = Image.open(file_to_upload)
		im1.save(buffer, "JPEG", quality=15)
	

# Rewrite compressed file	
		myfile2 = open(file_to_upload, 'w')
		myfile2.write(buffer.getvalue())
		myfile2.close()
		buffer.close()
			
# File size calculation                                                                                                
	        file_fd = open(file_to_upload, 'rb')                                                                           
	        file_fd.seek(0, os.SEEK_END)                                                                                   
	        size = file_fd.tell()                                                                                          
	        file_fd.seek(0)  

# Define command to open connection                                                                                    
	        if method == 0:                                                                                                
	                comm_send = 'AT+SQNHTTPSND=0,' + str(method) + ',"/' + process_script + '",' + str(size) + ',"2"' + r  
	        else:                                                                                                          
	                comm_send = 'AT+SQNHTTPSND=0,' + str(method) + ',"/' + file_to_upload + '",' + str(size) + ',"2"' + r  
  
# Connect to server and send data	
		print('Sending command ' + comm_send)
		channel0_at.write(comm_send)
		time.sleep(3)
		res = waiting_response('> ')
		if res == 0:
			sys.exit()
		print('Sending data ...')
		for i_byte in range(0, size):
			byte = file_fd.read(1)
			sys.stdout.write(str(i_byte+1)+"\r")
			channel0_at.write(byte)
			time.sleep(.0006)

		sys.stdout.write("\r\nTransfer complete.\r\n")

		time.sleep(1)
		res = waiting_response('OK')
		if res == 0:
			print('Something wrong, retry after 60 sec')
			time.sleep(60)

finally:
	print('Exit programm.')
	file_fd.close()
	channel0_at.close()

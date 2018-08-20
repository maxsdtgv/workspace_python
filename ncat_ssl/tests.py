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


uart2_console = "/dev/ttyXRUSB2"
uart2_console_speed = 115200

iii = ''
def queue_output(out, nqueue):
	#for line in iter(out.readline(), b''):
	global iii
	while True:	#	nqueue.put(line)

		for line in iter(out.readline, b''):
			nqueue.put(line.replace('\r','').replace('\n',''))
			time.sleep(.2)
		if iii != '':
			out.write(iii)
			iii = ''
		#out.close()

try:



	channel2_console = serial.Serial(uart2_console, uart2_console_speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port

	print('=================== Threads for uart readings')

	queue_console = Queue.Queue()

	thread_console = threading.Thread(target=queue_output, args=(channel2_console, queue_console))
	#thread_console.daemon = True # thread dies with the program
	thread_console.start()

	print('Done.')
	print('============================================')

	while True:
		#print(channel2_console.readline())
		time.sleep(.4)
		iii = '\r'
		if not queue_console.empty():

			line = queue_console.get()
			print(line)
finally:

	print('         Close uarts ...')
	channel2_console.close()





	
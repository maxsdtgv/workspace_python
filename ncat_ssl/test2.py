import threading
import serial
import time

connected = False
port = '/dev/ttyXRUSB2'
baud = 115200

serial_port = serial.Serial(port, baud, timeout=0)

def handle_data(data):
    print(data)

def read_from_port(ser):


	while True:
		print("test")
		time.sleep(.2)
		reading = ser.readline().decode()
		handle_data(reading)

thread = threading.Thread(target=read_from_port, args=(serial_port,))
thread.start()
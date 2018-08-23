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


uart0_at = "/dev/ttyXRUSB0"
uart0_at_speed = 921600

channel0_at = serial.Serial(uart0_at, uart0_at_speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port

#print('before = '+str(channel0_at))
#print(channel0_at)
#print(str(channel0_at.open))

print(channel0_at.isOpen())
channel0_at.close()
print('closed')


print(channel0_at.isOpen())
#print('    ')
#print('after = '+str(channel0_at))
#print(channel0_at)
#print(bool(channel0_at.open))
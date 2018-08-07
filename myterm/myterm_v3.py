import sys
import select
import tty
import termios
import serial
import time
import datetime

port = "/dev/ttyXRUSB0"
speed = 921600

time_o = 0
terminator = 0
fd = sys.stdin.fileno()
old = termios.tcgetattr(fd)
ser = serial.Serial(port, speed, timeout=0, parity=serial.PARITY_NONE)  # open serial port
#ser = serial.Serial(port, speed, timeout=0, parity=serial.PARITY_NONE, rtscts=1)  # open serial port

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def timest():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
    return st


try:
    tty.setcbreak(fd)
    print('')
    print('Port = %s') % port
    print('==================================== HELP KEYS ======================================')
    print('=          --- DTR toggling ---                                                     =')
    print('=  CTRL+I to set.dtr = True, voltage=0V                                             =')
    print('=  CTRL+O to set.dtr = False, voltage=1.8V                                          =')
    print('=          --- RTS toggling ---                                                     =')
    print('=  CTRL+U to set.rts = True, voltage=0V                                             =')
    print('=  CTRL+R to set.rts = False, voltage=1.8V                                          =')
    print('=                                                                                   =')
    print('=  CTRL+Y - on/off timestamp                                                        =')
    print('=                                                                                   =')
    print('=====================================================================================')
    while 1:
        s = ser.readlines()
        if s:
            for lines in s:
                # ss = lines.decode().replace('\n', '').replace('\r', '')
                ss = lines.decode()
                if lines.decode().find('\r') > -1:
                    terminator = 1
                else:
                    terminator = 0
                if time_o == 1 & terminator == 1:
                    sys.stdout.write('[' + timest() + '] ')
                sys.stdout.write(ss)
                sys.stdout.flush()
        if isData():
            c = sys.stdin.read(1)
            # print ord(c)
            if c == '\x09':  # x09 is CTRL+I
                ser.dtr = True
                print('>>> Service message >> CTRL+I pressed set.dtr = True, voltage=0V')
            elif c == '\x0F':  # x0F is CTRL+O
                ser.dtr = False
                print('>>> Service message >> CTRL+O pressed set.dtr = False, voltage=1.8V')
            elif c == '\x15':  # x0F is CTRL+U
                ser.rts = True
                print('>>> Service message >> CTRL+U pressed set.rts = TRUE, voltage=0V')
            elif c == '\x12':  # x0F is CTRL+R
                ser.rts = False
                print('>>> Service message >> CTRL+R pressed set.rts = FALSE, voltage=1.8V')
            elif c == '\x19':  # x19 is CTRL+Y - on/off timestamp
                if time_o == 0:
                    time_o = 1
                else:
                    time_o = 0
                print('>>> Service message >> CTRL+Y pressed - on/off timestamp toggled')
            elif c == '\x1b':  # x1b is ESC
                break

            else:
                ser.write(c.encode())

finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old)

import struct
import serial
import time
import datetime

try:
    millis = 0


    def timest():
        global millis
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        millis = int(round(time.time() * 1000))
        return st


    def parss():
        s = ser.readlines()
        out = ''
        for lines in s:
            out = lines.replace('\n', '').replace('\r', '')
            if out == 'OK':
                break
        return out


    ser = serial.Serial('/dev/ttyXRUSB1', 921600, timeout=0, parity=serial.PARITY_NONE, rtscts=1)  # open serial port
    d = struct.pack('BB', 0x0D, 0x0A)

    print('============================== Test for +SQNSCFG ========================================')
    av = 0
    for r in range(1, 7):
        #comm = 'AT'
        comm = 'AT+SQNSCFG=%d,0,456,111,600,20' % r
        ser.write(comm + d)                             # send command to port
        s1 = int(round(time.time() * 1000))             # first time point - before command
        print(timest() + ' Command try %d >> ' + comm) % (r)
        s = ''
        while s != 'OK':
            s = parss()
            time.sleep(0.001)

        s2 = int(round(time.time() * 1000))             # second time point - after command
        s3 = s2 - s1
        av += s3
        print(timest() + ' Command end OK %d >' + ' %d milliseconds') % (r, s3)
        time.sleep(3)
    print('\nAverage execution time for +SQNSCFG =' + ' %d milliseconds') % (av/6)
    print('============================================================================================\n')


    print('============================== Test for +SQNSCFGEXT ========================================')
    av = 0
    for r in range(1, 7):
        #comm = 'AT+SQNSS'
        comm = 'AT+SQNSCFGEXT=%d,1,1,77,0,0' % r
        ser.write(comm + d)                             # send command to port
        s1 = int(round(time.time() * 1000))             # first time point - before command
        print(timest() + ' Command try %d >> ' + comm) % (r)
        s = ''
        while s != 'OK':
            s = parss()
            time.sleep(0.001)

        s2 = int(round(time.time() * 1000))             # second time point - after command
        s3 = s2 - s1
        av += s3
        print(timest() + ' Command end OK %d >' + ' %d milliseconds') % (r, s3)
        time.sleep(3)
    print('\nAverage execution time for +SQNSCFGEXT =' + ' %d milliseconds') % (av/6)
    print('============================================================================================\n')
finally:
    ser.close()
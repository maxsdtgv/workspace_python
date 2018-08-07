import serial
import time
import datetime
import sys

tti = 0.03          # <<< timeout between sending seconds
try:
    def timest():
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
        return st

    def parss2():
        s = ser.readlines()
        qq = 0
        for lines in s:
            ss = lines.decode().replace('\n', '').replace('\r', '')
            print(ss)
            if ss == 'CONNECT':
                qq = 1
                break
            if ss == 'OK':
                qq = 2
                break
            if ss == 'NO CARRIER':
                qq = 3
                break
        return qq


    ser = serial.Serial('/dev/ttyXRUSB0', 921600, timeout=0, parity=serial.PARITY_NONE, rtscts=1)  # open serial port
    print(' Port = ' + ser.name)
    d = "\r"
    comm_0 = 'AT'
    comm_1 = 'AT+SQNSCFG=1,1,1,90,600,50'
    comm_2 = 'AT+SQNSD=1,0,3000,"192.168.3.1",0,,0'
    comm_3 = 'E'
    comm_4 = '+++'
    comm_5 = 'AT+SQNSH=1'
    comm_6 = 'AT+SQNSI'
    comm_7 = 'AT+SQNSS'
    comm_8 = 'ATE1'
    comm_0 += d
    comm_1 += d
    comm_2 += d
    comm_5 += d
    comm_6 += d
    comm_7 += d
    comm_8 += d
    err = 0
    print('=================================== Start tests ==================================================')
    ser.write(comm_0.encode())                 # ============== send AT
    time.sleep(3)
    parss2()
    ser.write(comm_8.encode())                 # ============== send ATE1
    time.sleep(3)
    parss2()
    ser.write(comm_1.encode())                 # ============== send AT+SQNSCFG=1,1,1,90,600,50
    time.sleep(3)
    parss2()
    ser.write(comm_2.encode())                 # ============== send
    time.sleep(4)
    b = 0

    if parss2() == 1:
        print 'Sending data (%s), timeout=%.2f' % (comm_3, tti)

        b = 0
        for i in range(1, 15000):
            ser.write(comm_3.encode())
            time.sleep(tti)
            cc = parss2()
            if (cc == 2) or (cc == 3):
                print 'Exit online mode (2) or NO CARRIER (3) code=%d\r\n' % cc
                err = 12
                break

            if b == 0:
                print('')
                sys.stdout.write(timest()+'-->')
                b = 100
            sys.stdout.write('.')
            b -= 1
    else:
        err = 12
        print('CONNECT Error!\r\n')

finally:
    if err != 12:
        print('')
        print('Sending +++')
        time.sleep(1)
        ser.write(comm_4.encode())  # ============ +++
        time.sleep(3)
        parss2()
        ser.write(comm_6.encode())  # ============ at+sqnsi
        time.sleep(1)
        parss2()
        ser.write(comm_7.encode())  # ============ at+sqnsi
        time.sleep(1)
        parss2()
        time.sleep(1)
        ser.write(comm_5.encode())  # =========== at+sqnsh=1
        time.sleep(1)
        parss2()
        ser.write(comm_7.encode())  # ============ at+sqnsi
        time.sleep(1)
        parss2()
        print('===================== Test end ============================')
    ser.close()

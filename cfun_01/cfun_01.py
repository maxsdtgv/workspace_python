import serial
import time
import datetime
import sys
import string

tti = 10  # <<< timeout between switching seconds
try:
    def timest():
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
        return st


    def parss3(ti):
        qq = 0
        for tu in range(0, ti):
            s = ser.readlines()
            for lines in s:
                ss = lines.decode().replace('\n', '').replace('\r', '')
                print(ss)
                if ss.startswith('OK'):
                    qq = 1
                    break
                if ss.startswith('+CEREG: 0'):
                    qq = 2
                    break
                if ss.startswith('+CEREG: 2'):
                    qq = 3
                    break
                if ss.startswith('+CEREG: 1,"0001","01A2D001",7'):
                    qq = 4
                    break
                if ss.startswith('+CFUN: 1'):
                    qq = 5
                    break
                if ss.startswith('+CFUN: 0'):
                    qq = 6
                    break
                if ss.startswith('+CFUN: 0'):
                    qq = 6
                    break
            time.sleep(1)
            if qq > 0:
                break
        return qq


    def parss4(ti, ts):
        qq = 0
        for tu in range(0, ti):
            s = ser.readlines()
            for lines in s:
                ss = lines.decode().replace('\n', '').replace('\r', '')
                print(ss)
                if ss.startswith(ts):

                    qq = 21
                    break
            if qq > 0:
                break
            time.sleep(1)
        return qq


    ser = serial.Serial('/dev/ttyUSB0', 921600, timeout=0, parity=serial.PARITY_NONE, rtscts=1)  # open serial port
    print(' Port = ' + ser.name)
    d = "\r"
    comm_0 = 'AT'
    comm_1 = 'AT+CFUN?'
    comm_2 = 'AT+CFUN=0'
    comm_3 = 'AT+CFUN=1'
    comm_4 = 'AT!="infoall"'
    comm_5 = 'AT^RESET'
    comm_6 = 'ATE1'
    comm_7 = 'AT+CEREG=1'
    comm_8 = 'AT+COPS?'
    comm_9 = 'AT+CEREG?'
    comm_10 = 'AT!="infoall"'
    comm_0 += d
    comm_1 += d
    comm_2 += d
    comm_3 += d
    comm_4 += d
    comm_5 += d
    comm_6 += d
    comm_7 += d
    comm_8 += d
    comm_9 += d
    comm_10 += d
    err = 0
    print('=================================== Start tests ==================================================')
    ser.write(comm_0.encode())  # ============== send AT
    time.sleep(1)
    parss3(1)

    ser.write(comm_6.encode())  # ============== send ATE1
    time.sleep(1)
    parss3(1)

    ser.write(comm_7.encode())  # ============== send AT+CEREG=1
    time.sleep(1)
    parss3(1)

    ser.write(comm_1.encode())  # ============== send AT+CFUN?
    time.sleep(1)

    if parss3(1) == 5:
        ser.write(comm_2.encode())  # ============== send AT+CFUN=0
        parss3(2)
        time.sleep(2)

    b = 0
    for i in range(1, 1200):
        print('=================================== Test start ===')
        sys.stdout.write(timest() + '-->')
        print('==== Test num %d ===' % i)
        ser.write(comm_10.encode())  # ============== send AT+CFUN=1
        cc = parss4(5, 'Pool 2:')
        ser.write(comm_3.encode())  # ============== send AT+CFUN=1
        cc = parss4(240, '+CEREG: 1')
        if cc == 21:
            sys.stdout.write(timest() + '-->')
            print('Network connected!\r\n')
        else:
            ser.write(comm_1.encode())  # ============== send AT+CFUN?
            time.sleep(1)
            parss3(2)
            ser.write(comm_9.encode())  # ============== send AT+CEREG?
            time.sleep(1)
            parss3(2)
            ser.write(comm_8.encode())  # ============== send AT+COPS?
            time.sleep(1)
            parss3(2)
            sys.stdout.write(timest() + '-->')
            print('Cant connect!!\r\n')
            ser.write(comm_4.encode())
            time.sleep(2)
            parss3(1)
            break
        ser.write(comm_2.encode())  # ============== send AT+CFUN=0
        time.sleep(2)
        parss3(2)

        print('=================================== Test end ===')
finally:
    print('')

    print('===================== Tests end ============================')
    ser.close()

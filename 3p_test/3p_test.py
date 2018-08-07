import serial
import time
import datetime
import sys
import string

test_ncat = 1
test_ppp = 0

t1min = 800
t1max = 1160
t1step = 20

t2min = 780
t2max = 1000
t2step = 20

t3min = 800
t3max = 1160
t3step = 20

tnum = 0

line_before = 'aaa'
plus = '+'
line_after = 'bbb'

try:
    def timest():
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
        return st


    def parss4(ti, ts):
        qq = 0
        for tu in range(0, ti):
            time.sleep(1)
            s = ser.readlines()
            for lines in s:
                ss = lines.decode().replace('\n', '').replace('\r', '')
                print(ss)
                if ts != '':
                    if ss.startswith(ts):
                        qq = 1
                        break
            if qq == 1:
                break
        return qq


    ser = serial.Serial('/dev/ttyXRUSB1', 921600, timeout=0, parity=serial.PARITY_NONE, rtscts=1)  # open serial port
    print(' Port = ' + ser.name)
    d = "\r"
    comm_0 = 'ATE'
    comm_1 = 'AT+SQNSD=1,0,1233,"192.168.3.1"'
    comm_2 = 'AT+SQNSO=1'
    comm_3 = 'AT+SQNSH=1'
    comm_4 = '+++'
    comm_5 = 'AT+CGDATA'
    comm_6 = 'ATO'
    comm_7 = 'ATH'
    comm_0 += d
    comm_1 += d
    comm_2 += d
    comm_3 += d
    comm_5 += d
    comm_6 += d
    comm_7 += d

    err = 0
    print('=================================== Start tests ==================================================')
    ser.write(comm_0.encode())  # ============== send AT
    parss4(3, '')
    if test_ncat == 1:
        print('======================== Test NCAT ============================================')
        ser.write(comm_1.encode())  # ============== send AT+SQNSD=1,0,1233,"192.168.3.1"
        time.sleep(1)
        if parss4(5, 'CONNECT') == 1:
            print('>>> Connect!!!')
            for t1 in range(t1min, t1max, t1step):
                for t2 in range(t2min, t2max, t2step):
                    for t3 in range(t3min, t3max, t3step):
                        tnum += 1

                        ser.write('\r\n' + str(tnum) + '  >> Params (ms) >> t1=' + str(t1) + ', t2=' + str(t2) + ', t3=' + str(t3) + ' >>> ' + line_before.encode()) % t1, t2, t3 # ============== send line before
                        ser.flush()
                        time.sleep(1.0*t1/1000)

                        ser.write(plus.encode())  # ============== send +
                        ser.flush()
                        time.sleep(1.0*t2/1000)
                        ser.write(plus.encode())  # ============== send +
                        ser.flush()
                        time.sleep(1.0*t2/1000)
                        ser.write(plus.encode())  # ============== send +
                        ser.flush()
                        time.sleep(1.0*t3/1000)
                        ser.write(line_after.encode())  # ============== send line after
                        ser.flush()
                        if parss4(2, 'OK') == 1:
                            print'%d Exit to command mode >>> %s (%dms) %s (%dms) %s (%dms) %s (%dms) %s' % (tnum, line_before, t1, plus, t2, plus, t2, plus, t3, line_after)
                            ser.write(d.encode())
                            parss4(1, '')
                            ser.write(comm_2.encode())
                            if parss4(2, 'CONNECT') == 1:
                                print('>>> Connect!!!')
                        else:
                            print'%d Stay in data mode >>> %s (%dms) %s (%dms) %s (%dms) %s (%dms) %s' % (tnum, line_before, t1, plus, t2, plus, t2, plus, t3, line_after)
        else:
            print('Connection error!!!')
    if test_ppp == 1:
        print('======================== Test PPP ============================================')
        ser.write(comm_5.encode())  # ============== send AT+CGDATA
        time.sleep(1)
        if parss4(5, 'CONNECT') == 1:
            print('>>> Connect!!!')
            for t1 in range(t1min, t1max, t1step):
                for t2 in range(t2min, t2max, t2step):
                    for t3 in range(t3min, t3max, t3step):
                        tnum += 1
                        ser.write(line_before.encode())  # ============== send line before
                        ser.flush()
                        time.sleep(1.0*t1/1000)

                        ser.write(plus.encode())  # ============== send +
                        ser.flush()
                        time.sleep(1.0*t2/1000)
                        ser.write(plus.encode())  # ============== send +
                        ser.flush()
                        time.sleep(1.0*t2/1000)
                        ser.write(plus.encode())  # ============== send +
                        ser.flush()

                        time.sleep(1.0*t3/1000)
                        ser.write(line_after.encode())  # ============== send line after
                        ser.flush()
                        if parss4(4, 'OK') == 1:
                            print'%d Exit to command mode >>> %s (%dms) %s (%dms) %s (%dms) %s (%dms) %s' % (tnum, line_before, t1, plus, t2, plus, t2, plus, t3, line_after)
                            ser.write(d.encode())
                            parss4(1, '')
                            ser.write(comm_6.encode())
                            if parss4(3, 'CONNECT') == 1:
                                print('>>> Connect!!!')
                        else:
                            print'%d Stay in data mode >>> %s (%dms) %s (%dms) %s (%dms) %s (%dms) %s' % (tnum, line_before, t1, plus, t2, plus, t2, plus, t3, line_after)
        else:
            print('Connection error!!!')

finally:
    print('Close connection ...')
    time.sleep(1)
    ser.write(comm_4.encode())
    if parss4(4, 'OK') == 1:
        ser.write(d.encode())
        parss4(1, '')
        ser.write(comm_3.encode())
        parss4(4, '')
        ser.write(comm_7.encode())
        parss4(4, '')
    print('===================== Tests end ============================')
    ser.close()

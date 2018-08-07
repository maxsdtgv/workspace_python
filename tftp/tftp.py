import struct
import serial
import time
import datetime




try:
    def timest():
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        return st


    def parss():
        s = ser.readlines()
        out = ''
        for lines in s:
            out = lines.replace('\n', '').replace('\r', '')
            if out != '':
                print(timest() + ' ==> ' + out)
            if (out == 'ERROR'):
                out = 'FAULT'
                break

        return out


    ser = serial.Serial('/dev/ttyXRUSB2', 921600, timeout=0, parity=serial.PARITY_NONE, rtscts=1)  # open serial port
    print(' Port = ' + ser.name)
    d = struct.pack('BB', 0x0D, 0x0A)
    #d = "\r\n"



    comm_conf1 = ['AT+SQNSCFG=4,3,0,0,100,50']
    comm_conf1 = ['AT+SQNSCFG=5,3,0,0,100,50']
    comm_conf2 = ['AT+SQNSCFGEXT=4,2,1,0,0,1']
    comm_conf2 = ['AT+SQNSCFGEXT=5,2,1,0,0,1']
    comm_estcn = ['AT+SQNSD=4,1,69,"10.1.11.31",0,52970,1']
    comm_estRX = ['AT+SQNSLUDP=5,1,52970']
    comm_req = ['AT+SQNSSENDEXT=4,28']
    REQ = "000174657374312E747874006F637465740074696D656F7574003500" # Request file test1.txt


    if init_clear == 1:
        print('=================================== Clear confs begin ===========================================')
        for i in range(1, 7):
            comm_rst = 'at+sqnscfg=%d,1,300,90,600,50' % i
            ser.write(comm_rst + d)
            time.sleep(5)
            parss()
            time.sleep(1)
        print('=================================== Clear confs end =============================================\n\n')

    print('=================================== Initial checks begin ========================================')
    for addc in comm_add:
        ser.write(addc + d)
        time.sleep(4)
        parss()
        time.sleep(1)
    print('=================================== Initial checks end ===========================================\n\n')

    print('=================================== Start tests ==================================================')
    for i in range(1, 7):
        for j in range(1, 9):

            comm_1 = 'at+sqnscfg=%d,%d,300,90,600,50' % (i, j)
            comm_2 = 'at+sqnsd=%d,0,80,"google.com",0,0,1' % i
            comm_3 = 'at+sqnsh=%d' % i

            ser.write(comm_1 + d)
            time.sleep(5)
            parss()
            time.sleep(1)

            ser.write(comm_2 + d)
            time.sleep(9)
            rrr = parss()
            time.sleep(1)
            if rrr == 'FAULT':
                print(timest() + ' ==> ' + 'EEERRROOORRR !!!!!!!!!!!!!!!!!!!!!!!! << HERE SHOULD BE OK')
                break
            if rrr == 'OK':
                ser.write(comm_3 + d)
                time.sleep(3)
                parss()
                time.sleep(1)
            print('=================================================')
        if rrr == 'FAULT':
            for addc in comm_add:
                ser.write(addc + d)
                time.sleep(3)
                parss()
                time.sleep(1)
            break

finally:
    ser.close()

#===============1. sudo python etm_icmpv6.py text_view_0.txt
#===============2. text2pcap -t "%H:%M:%S." text_view_0.txt.temp text_view_0.txt.temp.ngpcap'
#===============3. wireshark text_view_0.txt.temp.ngpcap

import sys
import os

str1 = 'ETM/ICMP6 - "Forwarded msg content'
str11 = 'ETM/SPY - DL'
str12 = 'ETM/SPY - UL'
str2 = 'ETM/ICMP6 - "(L='
str3 = '<END>'
tmps = ''
line = ''
flag_fwd_msg = 1
flag_spy = 1
num = 0
ss = ""
def getnewline():
    return file_in.readline().replace('\n', '').replace('\r', '')

def parse(substring):
    global num
    global ss
    tmps = ss[0:15].replace('.', '')+'0'
    tmps = tmps.replace("'", '.')
    num += 1
    print('%d Event found... >> %s %s') % (num, tmps, substring)                
    tmps += '\n'
    file_out.write(tmps)                #=============================change
    ss = '000000 ' + getnewline()

    while ss.find(str3) == -1:
        ss = ss.replace('  ', ' ') + ' '
        file_out.write(ss)
        ss = getnewline()
    file_out.write('\n')


try:
    file_in=open(sys.argv[1], 'r')
    print('Opening file >> %s') % sys.argv[1]
    file_out=open(sys.argv[1]+'.temp', 'w+')
    print('Output file >> %s') % sys.argv[1]+'.temp'
    fsize = os.path.getsize(sys.argv[1])
    while file_in.tell() < fsize:
        ss = getnewline()
        if ((ss.find(str1) > -1) and (flag_fwd_msg == 1)):
            ss = getnewline()
            if ss.find(str2) > -1:
                parse(str1)

        if (ss.find(str11) > -1) and (flag_spy == 1):
            parse(str11)

        if (ss.find(str12) > -1) and (flag_spy == 1):
            parse(str12) 

finally:
    file_in.close()
    file_out.close()
    print('=================================================')

print ('Next command >> text2pcap -t "%H:%M:%S." text_view_0.txt.temp text_view_0.txt.temp.ngpcap')



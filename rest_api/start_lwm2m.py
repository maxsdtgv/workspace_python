#!/usr/bin/python

########################################
#  env:    Python 2.7
#  file:   start_lwm2m.py
#  ver:    1
#  author: Maksym Vysochinenko
#  date:   9 oct 2018
########################################

import sys, getopt
sys.path.insert(0, "./modules")
import lwm2m_methods
import additional
import testcases

#============================ Configurable parameters (values could be changed) =====================================
imei = '004402280062922'
server = 'https://iotpf.mb.softbank.jp'
port = '7201'
headers = {	'Accept':'application/vnd.onem2m-res+json', 
			'Authorization':'Basic QzJERjdBMjg3LTUyMTYyZTM5OklvVCMyMDE4',
			'X-M2M-Origin':'C2DF7A287-52162e39',
			'X-M2M-RI':'{timestamp()}',
			'Content-Type':'application/vnd.onem2m-res+json;ty=4'
			}

#============================ System variables ======================================================================
url = server + ':' + port + '/IoT/imei:' + imei
campaign_file = ''

def campaign_arg(camp):
	try:
		opts, args = getopt.getopt(camp,"hc:",["cfile="])
	except getopt.GetoptError:
		print ('start_lwm2m.py -c <inputfile>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print ('Help:')
			print ('start_lwm2m.py -c <inputfile>')
			sys.exit()
		elif opt in ("-c", "--campaign"):
			inputfile = arg
	return inputfile

def campaign_list(campaign_name):
	cam_lines = []
	with open(campaign_name, "r") as fh:
		for line in fh:
			if line[0].isalpha():
				cam_lines.append(line.replace('\r', '').replace('\n', ''))
	fh.close()
	return cam_lines

def main():
	campaign_file = campaign_arg(sys.argv[1:])
	print 'Input campaign file is ', campaign_file
	tc_list = campaign_list(campaign_file)
	print 'List of TC', tc_list
	for tc in tc_list:
		tmp = getattr(testcases, tc)
		tmp()

if __name__ == '__main__':
	main()

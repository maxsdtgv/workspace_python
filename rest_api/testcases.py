#!/usr/bin/python

################################################
#  env:    Python 2.7
#  file:   testcases.py
#  ver:    1
#  author: Maksym Vysochinenko
#  date:   9 oct 2018
#  
#  File contain implementation of logic for
#  performing each test case
################################################
import sys, getopt
sys.path.insert(0, "./modules")
import lwm2m_methods
import additional


def tc01():
	print(additional.timest())
	ret = lwm2m_methods.read_single(3,0,1)
	print(ret['value'])
	return

def tc02():
	return

def tc03():
	return

def tc04():
	return

def tc05():
	return

def tc06():
	return

def tc07():
	return

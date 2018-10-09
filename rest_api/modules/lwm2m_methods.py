import requests
import json
import sys
sys.path.insert(0, "../")
import start_lwm2m

def read_single(obj, instance, param):
	full_url = start_lwm2m.url + '/' + str(obj) + '/' + str(instance) + '/' + str(param) + '/latest'
	resp = requests.get(full_url, headers = start_lwm2m.headers)
	temp = json.loads(resp.content)
	return {'status_code':resp.status_code, 'param':temp['m2m:cin']['con']['bn'] ,'value':temp['m2m:cin']['con']['e'][0]['sv']}

def read_multiple():
	return

def write_single():
	return

def write_multiple():
	return


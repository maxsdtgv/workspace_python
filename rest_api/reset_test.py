import requests
import json

resp = requests.get('https://iotpf.mb.softbank.jp:7201/IoT/imei:004402280062922/3/0/1/latest',headers = {'Accept':'application/vnd.onem2m-res+json', 'Authorization':'Basic QzJERjdBMjg3LTUyMTYyZTM5OklvVCMyMDE4','X-M2M-Origin':'C2DF7A287-52162e39','X-M2M-RI':'{timestamp()}','Content-Type':'application/vnd.onem2m-res+json;ty=4'})

print(str(resp.status_code))
if resp.status_code != 200:
    # This means something went wrong.
	raise ApiError('GET /tasks/ {}'.format(resp.status_code))
#print(resp.content)

#print(json.loads(resp.content))
t = json.loads(resp.content)
print(t['m2m:cin']['con']['e'][0]['sv'])
print(t['m2m:cin']['st'])
#for todo_item in resp.json():
#	print('{} {}'.format(todo_item['con'], todo_item['summary']))
#for todo_item in resp.content:
#	print(todo_item)
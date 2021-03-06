import requests
from kivymd.uix.snackbar import Snackbar

server_http = 'http://entity.ar:5000/' #'http://192.168.0.22:5000/'
base_url_http = server_http + 'graphql'#
base_url_ws = 'ws://entity.ar:5000/subscriptions'#'ws://192.168.0.22:5000/subscriptions'
headers = {'content-type': 'application/json'}

def send_payload(payload):
    try:
        print(payload)
        response = requests.post(base_url_http, headers=headers, data=payload)
        json = response.json()
        return json
    except:
        return False
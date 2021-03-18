from database import base


class variables(object):
    __doc__ = "class variables"

    server_http = 'http://entity.ar:5000/'  # 'http://192.168.0.22:5000/'
    base_url_http = server_http + 'graphql'  #
    base_url_ws = 'ws://entity.ar:5000/subscriptions'  # 'ws://192.168.0.22:5000/subscriptions'
    headers = {'content-type': 'application/json'}








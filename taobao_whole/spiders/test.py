import urllib
import requests
import re
import socket
# print(socket.gethostbyname(socket.gethostname()))

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 0))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

print(get_ip())

# url = 'https://s.taobao.com/search?q=%E5%AE%B6%E5%BA%AD%E4%BF%9D%E5%81%A5&s=1892&sort=sale-desc'
# print(urllib.parse.unquote(url))

# st = '123人收货'
# print(re.search('\d+',st).group())
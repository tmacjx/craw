import requests

# http://60.169.124.31:32247

ip, port = '113.121.174.4', 26791

proxy_url = "{2}://{0}:{1}".format(ip, port, str('http').lower())

http_url = "https://www.baidu.com"

proxy_dict = {
	"http": proxy_url,
}

response = requests.get(http_url, proxies=proxy_dict)

print(response)
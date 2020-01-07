# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent

class CrawSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CrawDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random


# 批量拦截所有的请求和响应
# class MiddlewearproDownloaderMiddleware(object):
#     # UA池
#     user_agent_list = [
#         "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
#         "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
#         "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
#         "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
#         "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
#         "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
#         "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
#         "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
#         "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
#         "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
#         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
#         "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
#         "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
#         "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
#         "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
#         "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
#         "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
#         "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
#         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
#         "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
#         "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
#         "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
#         "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
#         "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
#         "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
#         "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
#         "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
#         "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
#         "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
#         "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
#         "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
#         "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
#         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
#         "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
#         "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
#         "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
#     ]
#     # 代理池
#     PROXY_http = [
#         '153.180.102.104:80',
#         '195.208.131.189:56055',
#     ]
#     PROXY_https = [
#         '120.83.49.90:9000',
#         '95.189.112.214:35508',
#     ]
#
#     # 拦截正常请求：request就是该方法拦截到的请求，spider就是爬虫类实例化的一个对象
#     def process_request(self, request, spider):
#         print('this is process_request!!!')
#         # UA伪装
#         headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
#                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 ',
#                    'Connection': 'keep-alive'}
#         # {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'python-requests/2.18.4',
#         #  'Connection': 'keep-alive'}
#         request.headers['User-Agent'] = headers['User-Agent']
#         request.headers['Accept'] = headers['Accept']
#         request.headers['Accept-Encoding'] = headers['Accept-Encoding']
#         request.headers['Connection'] = headers['Connection']
#         # request.headers['User-Agent'] = random.choice(self.user_agent_list)
#         # request.headers['Accept'] = '*/*'
#         # request.headers['Connection'] = 'keep-alive'
#         # request.headers['Accept-Encoding'] = 'gzip, deflate'
#         # # request.meta['proxy'] = 'http://'+ random.choice(self.PROXY_http)
#         # print(request.headers)
#
#     # 拦截所有的响应
#     def process_response(self, request, response, spider):
#
#         return response
#
#     # 拦截发生异常的请求对象
#     def process_exception(self, request, exception, spider):
#         print('this is process_exception!!!!')
#         # 代理ip的设定
#         if request.url.split(':')[0] == 'http':
#             request.meta['proxy'] = random.choice(self.PROXY_http)
#         else:
#             request.meta['proxy'] = random.choice(self.PROXY_https)
#
#         # 将修正后的请求对象重新进行请求发送
#         return request


from fake_useragent import UserAgent
import requests


class RandomUserAgent(object):

    def process_request(self, request, spider):
        ua = UserAgent(verify_ssl=False)
        request.headers['Accept-Encoding'] = 'gzip, deflate'
        request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        request.headers['Connection'] = 'keep-alive'
        request.headers['Referer'] = 'http://www.kc0011.net'
        request.headers['Host'] = 'kc0011.net'
        request.headers['Upgrade-Insecure-Requests'] = 1
        request.headers['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
        request.headers['User-Agent'] = ua.random

    def process_response(self, request, response, spider):

        return response


from .utils import redis_client
from .ip_utils import IPUtil

ip_util = IPUtil()


class ProxyMiddleware(object):
    def __init__(self, ip):
        self.ip = ip

    @classmethod
    def from_crawler(cls, crawler):
        return cls(ip=crawler.settings.get('PROXIES'))

    def process_request(self, request, spider):
        proxy_ip = ip_util.get_random_ip()
        spider.logger.debug('using ip proxy: %s' % proxy_ip)
        request.meta["proxy"] = proxy_ip

    def process_response(self, request, response, spider):
        # 如果返回的response状态不是200，重新生成当前request对象
        if response.status != 200:
            ip_util.create_new_ip()
            proxy_ip = ip_util.get_random_ip()
            # 对当前reque加上代理
            spider.logger.debug("change Proxy: %s" % proxy_ip)
            request.meta['proxy'] = proxy_ip
            return request
        return response

    def del_ip(self, proxy):
        # 删除无效的ip
        redis_client.rpop('kc_ip')

    # def process_exception(self, request, exception, spider):
    #     proxy_ip = ip_util.get_random_ip()
    #     spider.logger.debug('change using ip proxy: %s' % proxy_ip)
    #     request.meta["proxy"] = proxy_ip
    #     return request


class ProxyStaticMiddleware(object):
    def __init__(self, proxy):
        self.proxy = proxy

    @classmethod
    def from_crawler(cls, crawler):
        return cls(proxy=crawler.settings.get('PROXIES'))

    def process_request(self, request, spider):
        proxy = random.choice(self.proxy)
        spider.logger.debug('change using ip proxy: %s' % proxy)
        request.meta['proxy'] = 'http://{}'.format(proxy)


# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random

from fake_useragent import UserAgent
import requests

from .utils import redis_client
from .ip_utils import IPUtil
import time

class RandomUserAgent(object):

    def process_request(self, request, spider):
        ua = UserAgent(verify_ssl=False)
        request.headers['Accept-Encoding'] = 'gzip, deflate'
        request.headers['Connection'] = 'keep-alive'
        request.headers['Referer'] = 'http://www.kc0011.net'
        request.headers['Host'] = 'kc0011.net'
        request.headers['Upgrade-Insecure-Requests'] = 1
        request.headers['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
        request.headers['User-Agent'] = ua.random

    def process_response(self, request, response, spider):
        return response


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
            spider.logger.debug('非200 change %s %s' % (response.status, response.url))
            if response.status in [503, 500, 404]:
                time.sleep(10)
            proxy_ip = ip_util.get_random_ip()
            # 对当前request加上代理
            spider.logger.debug("change Proxy: %s" % proxy_ip)
            request.meta['proxy'] = proxy_ip
            return request
        return response

    def del_ip(self, proxy):
        # 删除无效的ip
        redis_client.rpop('kc_ip')

    def process_exception(self, request, exception, spider):
        spider.logger.debug('process exception %s %s' % (exception, requests))
        proxy_ip = ip_util.get_random_ip()
        spider.logger.debug('change using ip proxy: %s' % proxy_ip)
        request.meta["proxy"] = proxy_ip
        return request


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


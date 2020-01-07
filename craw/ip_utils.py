#!/usr/bin/env python
# encoding: utf-8
"""
@author: yousheng
@contact: 1197993367@qq.com
@site: http://youyuge.cn

@version: 1.0
@license: Apache Licence
@file: crawl_ip.py
@time: 17/9/27 下午3:06

"""
import requests
from queue import Queue


class PoolException(Exception):
    pass


class Pool(object):
    '''一个数据库连接池'''

    def __init__(self, maxActive=5, maxWait=None, init_size=0, db_type="SQLite3", **config):
        self.__freeConns = Queue(maxActive)
        self.maxWait = maxWait
        self.db_type = db_type
        self.config = config
        if init_size > maxActive:
            init_size = maxActive
        for i in range(init_size):
            self.free(self._create_conn())

    def __del__(self):
        print("__del__ Pool..")
        self.release()

    def release(self):
        '''释放资源，关闭池中的所有连接'''
        print("release Pool..")
        while self.__freeConns and not self.__freeConns.empty():
            con = self.get()
            con.release()
        self.__freeConns = None

    def _create_conn(self):
        '''创建连接 '''
        if self.db_type in dbcs:
            return dbcs[self.db_type](**self.config)

    def get(self, timeout=None):
        '''获取一个连接
        @param timeout:超时时间
        '''
        if timeout is None:
            timeout = self.maxWait
        conn = None
        if self.__freeConns.empty():  # 如果容器是空的，直接创建一个连接
            conn = self._create_conn()
        else:
            conn = self.__freeConns.get(timeout=timeout)
        conn.pool = self
        return conn

    def free(self, conn):
        """
        将一个连接放回池中
        :return:
        """
        conn.pool = None
        if self.__freeConns.full():  # 如果当前连接池已满，直接关闭连接
            conn.release()
            return
        self.__freeConns.put_nowait(conn)


from abc import ABCMeta, abstractmethod


class PoolingConnection(object):
    def __init__(self, **config):
        self.conn = None
        self.config = config
        self.pool = None

    def __del__(self):
        self.release()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def release(self):
        print("release PoolingConnection..")
        if self.conn is not None:
            self.conn.close()
            self.conn = None
        self.pool = None

    def close(self):
        if self.pool is None:
            raise PoolException("连接已关闭")
        self.pool.free(self)

    def __getattr__(self, val):
        if self.conn is None and self.pool is not None:
            self.conn = self._create_conn(**self.config)
        if self.conn is None:
            raise PoolException("无法创建数据库连接 或连接已关闭")
        return getattr(self.conn, val)

    @abstractmethod
    def _create_conn(self, **config):
        pass


class SQLit3PoolConnection(PoolingConnection):
    def _create_conn(self, **config):
        import sqlite3
        return sqlite3.connect(**config)

import pymysql

from craw.settings import MYSQL_HOST, MYSQL_DATABASE, MYSQL_PASSWORD, MYSQL_USER, MYSQL_PORT
# MYSQL_HOST = ""
# MYSQL_DATABASE = 'bbs'
# MYSQL_USER = 'class'
# MYSQL_PASSWORD = 'mypwd'
# MYSQL_PORT = 3306


db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, charset='utf8', port=MYSQL_PORT)
cursor = db.cursor()


import logging

logger = logging.getLogger("logger")

file_handler = logging.FileHandler(filename="fetch.log")
logger.setLevel(logging.DEBUG)

logger.addHandler(file_handler)

import time


# ip的管理类
class IPUtil(object):
    # noinspection SqlDialectInspection
    def create_new_ip(self):
        url = "http://api.xdaili.cn/xdaili-api//privateProxy/getDynamicIP/DD2020175186iTjDQ8/3403f3ebfff111e7bcaf7cd30abda612?returnType=2"
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            ip_list = []
            if result['ERRORCODE'] == '0':
                data = result['RESULT']
                ip = (data.get('wanIp'), data.get('proxyport'))
                ip_list.append(ip)
            else:
                time.sleep(15)
            for item in ip_list:
                ip, port = item
                sql = "insert into proxy_ip(ip, port) values ('{0}', '{1}')".format(ip, port)
                cursor.execute(sql)
                db.commit()
                logger.info('更新ip库成功')

    def get_random_ip(self):
        # 从数据库中随机获取一个可用的ip
        # before = datetime.datetime.now() - datetime.timedelta(minutes=3)
        # temp_time = datetime.datetime.strftime(before, "%Y-%m-%d %H:%M:%S")
        # random_sql = 'select ip, port from proxy_ip where  ORDER BY RAND() LIMIT 1;' % (temp_time, )
        # random_sql = 'select ip, port from proxy_ip  ORDER BY RAND() LIMIT 1;'
        random_sql = 'select ip, port from proxy_ip  ORDER BY create_time desc LIMIT 1;'

        # random_sql = """
        #  SELECT ip, port FROM proxy_ip
        #   ORDER BY RAND()
        #   LIMIT 1
        # """
        cursor.execute(random_sql)

        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]

            judge_re = self.judge_ip(ip, port)
            if judge_re:
                res = "http://{0}:{1}".format(ip, port).lower()
                logger.debug('valid ip %s' % res)
                return res
            else:
                return self.get_random_ip()

    def judge_ip(self, ip, port, ip_type='http'):
        # 判断ip是否可用，如果通过代理ip访问百度，返回code200则说明可用
        # 若不可用则从数据库中删除
        print('begin judging ---->', ip, port, ip_type)
        http_url = "https://www.baidu.com"
        proxy_url = "{2}://{0}:{1}".format(ip, port, str(ip_type).lower())
        try:
            proxy_dict = {
                "http": proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            logger.debug("invalid ip and port,cannot connect baidu")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                logging.debug('effective ip')
                return True
            else:
                logger.debug("invalid ip and port,code is " + str(code))
                self.delete_ip(ip)
                return False

    # noinspection SqlDialectInspection
    def delete_ip(self, ip):
        # 从数据库中删除无效的ip
        delete_sql = "delete from proxy_ip where ip='{0}'".format(ip)
        cursor.execute(delete_sql)
        db.commit()
        logger.debug('删除ip')
        return True


if __name__ == '__main__':
    IPUtil().get_random_ip()
    # ip = IPUtil()
    # for i in range(20):

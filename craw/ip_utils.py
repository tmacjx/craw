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
import pymysql
import logging
import time
from craw.utils import redis_client
from craw.settings import \
    MYSQL_HOST, MYSQL_DATABASE, MYSQL_PASSWORD, MYSQL_USER, MYSQL_PORT


logger = logging.getLogger("logger")

file_handler = logging.FileHandler(filename="fetch.log")
logger.setLevel(logging.DEBUG)

logger.addHandler(file_handler)


db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, charset='utf8', port=MYSQL_PORT)
cursor = db.cursor()


# ip的管理类
class IPUtil(object):
    def create_new_ip(self):
        # 并发的情况，存在竞争获取代理的情况
        lock = redis_client.acquire_lock(timeout=60 * 3)
        if lock:
            logger.debug('获取lock成功')
            # time.sleep(8)
            url = "http://api.xdaili.cn/xdaili-api//privateProxy/applyStaticProxy?spiderId=4c43a47073f344bab15a4a3ddfff23ea&returnType=2&count=1"
            while 1:
                response = requests.get(url)
                if response.status_code == 200:
                    result = response.json()
                    if result['ERRORCODE'] == '0':
                        data = result['RESULT']
                        for item in data:
                            ip, port = item.get('ip'), item.get('port')
                            sql = "insert into proxy_ip(ip, port) values ('{0}', '{1}')".format(ip, port)
                            cursor.execute(sql)
                            db.commit()
                            logger.info('更新ip库成功')
                        redis_client.release_lock()
                        logger.debug('释放lock')
                        return True
                    else:
                        logger.debug('fail %s' % result)
                        time.sleep(15)
        else:
            logger.debug('获取lock失败')
            time.sleep(10)
            return False

    def get_random_ip(self):
        # 从数据库中随机获取一个可用的ip
        # before = datetime.datetime.now() - datetime.timedelta(minutes=5)
        # temp_time = datetime.datetime.strftime(before, "%Y-%m-%d %H:%M:%S")
        # random_sql = 'select ip, port from proxy_ip  ORDER BY id desc LIMIT 10;'
        # random_sql = 'select ip, port from proxy_ip where create_time >= "%s" ORDER BY RAND() LIMIT 5;' % (temp_time, )
        # random_sql = 'select ip, port from proxy_ip  ORDER BY RAND() LIMIT 1;'
        random_sql = 'select ip, port from proxy_ip  ORDER BY id desc LIMIT 1;'

        # random_sql = """
        #  SELECT ip, port FROM proxy_ip
        #   ORDER BY RAND()
        #   LIMIT 1
        # """
        cursor.execute(random_sql)
        result = cursor.fetchall()
        if not result:
            self.create_new_ip()
            return self.get_random_ip()
        else:
            for ip_info in result:
                ip = ip_info[0]
                port = ip_info[1]

                judge_re = self.judge_ip(ip, port)
                if judge_re:
                    res = "http://{0}:{1}".format(ip, port).lower()
                    logger.debug('valid ip %s' % res)
                    return res
            self.create_new_ip()
            return self.get_random_ip()

    def judge_ip(self, ip, port, ip_type='http'):
        # 判断ip是否可用，如果通过代理ip访问百度，返回code200则说明可用
        # 若不可用则从数据库中删除
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

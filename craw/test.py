
import requests
import time
import logging
import os, sys

logger = logging.getLogger("logger")

file_handler = logging.FileHandler(filename="ip.log")
logger.setLevel(logging.DEBUG)
import pymysql
logger.addHandler(file_handler)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

sys.path.append(BASE_DIR)

from craw.settings import MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_HOST


db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, charset='utf8', port=MYSQL_PORT)
cursor = db.cursor()


def crawl_xici_ip():
    '''
    爬取一定页数上的所有代理ip,每爬完一页，就存入数据库
    :return:
    '''
    url = "http://api.xdaili.cn/xdaili-api//privateProxy/getDynamicIP/DD2020175186iTjDQ8/e140cb7c529711e8bcaf7cd30abda612?returnType=2"
    # while 1:
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

        # # 每页提取完后就存入数据库
        # for ip_info in ip_list:
        #     cursor.execute(
        #         "insert proxy_ip(ip, port, type, speed, alive) VALUES('{0}', '{1}', '{2}', {3}, '{4}')".format(
        #             ip_info[0], ip_info[1], ip_info[2], ip_info[3], ip_info[4]
        #         )
        #     )
        #
        #     conn.commit()


if __name__ == '__main__':
    crawl_xici_ip()
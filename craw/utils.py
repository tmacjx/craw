"""
# @Author  wk
# @Time 2019/12/19 22:55

"""
import re
import time
import threading
from redis import ConnectionPool, StrictRedis
from redis.sentinel import Sentinel


def is_phone(number):
    """
    判断是否是手机号
    :param number:
    :return:
    """
    reg = "1[3|4|5|7|8][0-9]{9}"
    return re.findall(reg, number)


def is_fix_phone(number):
    """
    判断是否是固话
    :param number:
    :return:
    """
    res = re.match("\d{3}-\d{8}|\d{4}-\d{7}", number)
    if res is not None:
        return True
    return False


def search_phone(text):
    phone = re.findall(r'1[34578]\d{9}', text)
    if len(phone) == 1:
        return phone[0], None
    elif len(phone) >= 2:
        return phone[0], phone[1]
    else:
        return None, None


def search_fix_phone(text):
    fix_phone = re.findall("\d{3}-\d{8}|\d{4}-\d{7}", text)
    if len(fix_phone) > 0:
        return fix_phone[0]
    return None


class RedisInterface(object):
    # serializer = pickle

    def __init__(self, redis_config, password, master=None, connect_type='direct', db=0):
        """
        :param redis_config:
        :param password:
        :param master:
        :param connect_type: 连接方式 direct: 直连 sentinel: 哨兵
        """
        self.redis_config = redis_config
        self.password = password
        self.master = master
        self.db = db
        self.connect_type = connect_type
        self.redis = None
        self.host, self.port = self.redis_config[0]
        self._connect()

    def _connect(self):
        # 直接
        if self.connect_type == 'direct':
            self.pool = ConnectionPool(host=self.host, port=self.port, password=self.password, db=self.db,
                                       max_connections=200, socket_keepalive=True, decode_responses=True)
            # StrictRedis
            self.redis = StrictRedis(connection_pool=self.pool)
        # 哨兵
        else:
            # 哨兵连接池
            self.sentinel = Sentinel(self.redis_config, password=self.password, socket_timeout=3, db=self.db,
                                     socket_keepalive=True, decode_responses=True)
            self.redis = self.sentinel.master_for(self.master, max_connections=200)

    def keep_alive(self):
        """
        保持客户端长连接
        """
        ka_thread = threading.Thread(target=self._ping)
        ka_thread.start()

    def _ping(self):
        """
        发个消息，刷存在感
        """
        while True:
            time.sleep(60)
            # 尝试向redis-server发一条消息
            if not self._connect().ping():
                del self.sentinel
                self.sentinel = Sentinel(self.redis_config, socket_timeout=0.1, password=self.password)
                self.redis = self.sentinel.master_for(self.master, socket_timeout=0.1)

    def set_in(self, item, key="user_set"):
        is_exist = self.redis.sismember(key, item)
        if is_exist:
            print('redis user存在')
            return True
        else:
            return False

    def set_add(self, item, key="user_set"):
        res = self.redis.sadd(key, item)
        print('redis 暂存user %s' % res)
        return res

    def lpush(self, key, item):
        return self.redis.lpush(key, item)

    def pfadd(self, key, item):
        return self.redis.pfadd(key, item)


redis_config = [('34.92.7.151', 6379), ]
redis_password = '123456'

redis_client = RedisInterface(redis_config, redis_password)




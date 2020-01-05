"""
# @Author  wk
# @Time 2019/12/22 12:35

"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis

# todo sqlite
# 初始化数据库连接:
engine = create_engine('mysql+mysqlconnector://root:root@localhost:3306/spider')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
# 初始化redis数据库连接
Redis = redis.StrictRedis(host='localhost', port=6379, db=0)


"""
# @Author  wk
# @Time 2019/12/22 12:32

"""

from sqlalchemy import Column, String, Integer, DateTime, TEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'post_user'
    id = Column(Integer, primary_key=True)
    userid = Column(String, unique=True)
    # 姓名
    name = Column(String)
    # 地址
    address = Column(String)
    # 固定电话
    fixed_phone = Column(String)
    # 手机1
    phone_1 = Column(String)
    phone_2 = Column(String)
    # 交易等级
    trade_level = Column(String)
    # 信用积分
    credit_score = Column(Integer)
    # 评分次数
    score_count = Column(Integer)
    # 发帖次数
    post_count = Column(Integer)
    # 发帖积分
    post_score = Column(Integer)
    # 注册时间
    register_time = Column(DateTime)
    # 认证员注明
    remark = Column(TEXT)
    # 警告原因
    warning_reason = Column(TEXT)

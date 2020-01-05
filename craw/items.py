# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    # define the fields for your item here like:
    # 账户id
    userid = scrapy.Field()
    # 姓名
    name = scrapy.Field()
    # 地址
    address = scrapy.Field()
    # 固定电话
    fixed_phone = scrapy.Field()
    # 手机1
    phone_1 = scrapy.Field()
    phone_2 = scrapy.Field()
    # 交易等级
    trade_level = scrapy.Field()
    # 信用积分
    credit_score = scrapy.Field()
    # 评分次数
    score_count = scrapy.Field()
    # 发帖次数
    post_count = scrapy.Field()
    # 发帖积分
    post_score = scrapy.Field()
    # 注册时间
    register_time = scrapy.Field()
    # 认证员注明
    remark = scrapy.Field()
    # 警告原因
    warning_reason = scrapy.Field()


class CategoryUserItem(scrapy.Item):
    category_name = scrapy.Field()
    userid = scrapy.Field()

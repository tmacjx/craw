# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
import pymysql
from .items import UserItem, CategoryUserItem
import sqlite3
from .utils import redis_client

logger = logging.basicConfig(
        filename='log.txt',
        level=logging.DEBUG
    )


class CrawPipeline(object):
    def process_item(self, item, spider):
        return item


# # 去重
# class DuplicatesPipeline(object):
#     def process_item(self, item, spider):
#         if Redis.exists('url:%s' % item['url']):
#             raise DropItem("Duplicate item found: %s" % item)
#         else:
#             Redis.set('url:%s' % item['url'],1)
#             return item


class SQLitePipeline(object):

    # 打开数据库
    def open_spider(self, spider):
        db_name = spider.settings.get('SQLITE_DB_NAME', 'scrapy.db')
        self.db_conn = sqlite3.connect(db_name)
        self.db_cur = self.db_conn.cursor()
        self.logger = spider.logger

    # 关闭数据库
    def close_spider(self, spider):
        self.db_conn.commit()
        self.db_conn.close()

    # 对数据进行处理
    def process_item(self, item, spider):
        if isinstance(item, UserItem):
            self.insert_user(item)
        elif isinstance(item, CategoryUserItem):
            self.insert_category(item)
        else:
            return item

    def insert_category(self, item):
        try:
            values = (
                item['userid'],
                item['category_name'],
            )

            sql = 'INSERT INTO category_user VALUES(?, ?)'
            self.db_cur.execute(sql, values)
            self.db_conn.commit()
        except Exception as e:
            self.db_conn.rollback()
            self.logger.error('写入栏目 error %s' % e, exc_info=True)
        self.logger.debug('success inset cate')

    # 插入数据
    def insert_user(self, item):
        try:
            values = (
                item['userid'],
                item.get('name', '未注明'),
                item.get('address', ''),
                item.get('fixed_phone', ''),
                item.get('phone_1', ''),
                item.get('phone_2', ''),
                item.get('trade_level', ''),
                int(item['credit_score']),
                int(item['score_count']),
                int(item['post_count']),
                int(item['post_score']),
                item['register_time'],
                item.get('remark', ''),
                item.get('warning_reason', '')
            )
            sql = 'INSERT INTO post_user VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )'

            self.db_cur.execute(sql, values)
            self.db_conn.commit()
        except Exception as e:
            self.db_conn.rollback()
            self.logger.error('写入用户error %s' % e, exc_info=True)
        else:
            # 暂存到redis中
            redis_client.set_add(item['userid'])
            self.logger.debug('success insert user')


class MysqlPipeline(object):
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT'),
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()

    # def process_item(self, item, spider):
    #     data = dict(item)
    #     keys = ', '.join(data.keys())
    #     values = ', '.join(['%s'] * len(data))
    #     sql = 'insert into %s (%s) values (%s)' % (item.table, keys, values)
    #     self.cursor.execute(sql, tuple(data.values()))
    #     self.db.commit()
    #     return item

    def process_item(self, item, spider):
        if isinstance(item, UserItem):
            self.insert_user(item, spider)
        elif isinstance(item, CategoryUserItem):
            self.insert_category(item, spider)
        else:
            return item

    def insert_category(self, item, spider):
        try:
            values = (
                item['userid'],
                item['category_name'],
            )

            sql = 'INSERT INTO category_user (userid, category_name)VALUES("%s", "%s")' % (values[0], values[1])
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            spider.logger.error('写入栏目 error %s' % e, exc_info=True)
        spider.logger.debug('success inset cate')

        # 插入数据

    def insert_user(self, item, spider):
        try:
            values = (
                item['userid'],
                item.get('name', "未注明"),
                item.get('address', ""),
                item.get('fixed_phone', ""),
                item.get('phone_1', ""),
                item.get('phone_2', ""),
                item.get('trade_level', ""),
                int(item['credit_score']),
                int(item['score_count']),
                int(item['post_count']),
                int(item['post_score']),
                item['register_time'],
                item.get('remark', ""),
                item.get('warning_reason', "")
            )
            sql = 'INSERT INTO post_user (userid, name, address, fixed_phone, phone_1, phone_2, ' \
                  'trade_level, credit_score, score_count, post_count, post_score, register_time, ' \
                  'remark, warning_reason)' \
                  'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )'

            self.cursor.execute(sql, values)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            spider.logger.error('写入用户error %s' % e, exc_info=True)
        else:
            # 暂存到redis中
            redis_client.set_add(item['userid'])
            spider.logger.debug('success insert user')


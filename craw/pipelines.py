# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
from items import UserItem, CategoryUserItem
import sqlite3
from utils import redis_client

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
            print('error', e)
        print('success inset cate')

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
            print('success insert user')



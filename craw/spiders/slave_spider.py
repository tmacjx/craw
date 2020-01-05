"""
# @Author  wk
# @Time 2019/12/17 22:48
"""
import scrapy
import re
from utils import search_fix_phone, search_phone

from items import UserItem, CategoryUserItem
from utils import redis_client
from scrapy_redis.spiders import RedisCrawlSpider, RedisSpider

SITE_URL = "http://www.kc0011.net"

user_list = []

IGNORE_TITLE = ('投诉暴光台', '交易视点', '中介支付专栏')

# class DetailSpider(scrapy.Spider):
#     name = "detail"
#     handle_httpstatus_list = [200, 400]
#     start_urls = [
#         "http://www.kc0011.net",
#         # 'http://www.kc0011.net/?boardid=126&action=&topicmode=0&page=2',
#         # 'http://www.kc0011.net/?boardid=149&action=&topicmode=0&page=2',
#     ]
#
#     def parse(self, response):
#         """
#         分析主页
#         :param response:
#         :return:
#         """
#         self.logger.debug('主页parse---')
#         for sel in response.xpath('//body/div[contains(@class, "mainbar")][last()-6]'):
#             title_sel = sel.xpath('./div/div[last()-1]')[1].xpath('./a')
#             title = title_sel.xpath('./text()').extract()[0]
#             self.logger.debug('主页parse 栏目: %s' % title)
#             category_pages = title_sel.xpath('./@href')
#             if category_pages:
#                 category_page = urljoin(SITE_URL, category_pages[0].extract())
#                 self.logger.debug('主页parse 栏目URL: %s' % category_pages)
#                 yield scrapy.Request(category_page, callback=self.parse_category_url)
#
#         for sel in response.xpath('//body/div[contains(@class, "mainbar")][last()-8]'):
#             title_sel = sel.xpath('./div/div[last()-1]')[1].xpath('./a')
#             title = title_sel.xpath('./text()').extract()[0]
#             self.logger.debug('主页parse 栏目: %s' % title)
#             category_pages = title_sel.xpath('./@href')
#             if category_pages:
#                 category_page = urljoin(SITE_URL, category_pages[0].extract())
#                 self.logger.debug('主页parse 栏目URL: %s' % category_pages)
#                 yield scrapy.Request(category_page, callback=self.parse_category_url)
#
#         for sel in response.xpath('//body/div[contains(@class, "mainbar") and contains(@style,"height:60px") '
#                                   'and contains(@style,"line-height:18px")]'):
#             category_title = sel.xpath('./div/div/a')
#             for title_sel in category_title:
#                 title = title_sel.xpath('./text()').extract()[0]
#                 if title in IGNORE_TITLE:
#                     continue
#                 self.logger.debug('主页parse 栏目: %s' % title)
#                 category_pages = title_sel.xpath('./@href')
#                 if category_pages:
#                     category_page = urljoin(SITE_URL, category_pages[0].extract())
#                     self.logger.debug('主页parse 栏目URL: %s' % category_pages)
#                     yield scrapy.Request(category_page, callback=self.parse_category_url)
#
#     def parse_category_url(self, response):
#         """
#         分析栏目列表
#         :param response:
#         :return:
#         """
#         self.logger.debug('栏目parse---')
#         for post_sel in response.xpath('/html/body/form[1]/div[@class="list"]/div[@class="listtitle"]/a'):
#             post_pages = post_sel.xpath('./@href')
#             if post_pages:
#                 post_page = SITE_URL + '/' + post_pages[0].extract()
#                 # post_page = urljoin(SITE_URL, post_pages[0].extract())
#                 self.logger.debug('栏目parse 文章URL: %s' % post_page)
#                 yield scrapy.Request(post_page, callback=self.parse_post_url)
#
#         page_links = response.xpath('/html/body/div[@class="mainbar0"][last()-1]/div[1]/table[1]/form[1]/tr/td')
#         cur_index = 1
#         # 找到当前页
#         for index, link in enumerate(page_links):
#             current_link = link.xpath('./font')
#             if current_link:
#                 cur_index = index
#                 break
#         next_link = page_links[cur_index + 1]
#         # 判断下一个元素 是否是下一页
#         next_pages = next_link.xpath('./a/@href')
#         if next_pages:
#             next_page = SITE_URL + '/' + next_pages[0].extract()
#             # next_page = urljoin(SITE_URL, next_pages[0].extract())
#             self.logger.debug('栏目parse 下一页: %s' % next_page)
#             yield scrapy.Request(next_page, callback=self.parse)
#         else:
#             self.logger.debug('栏目parse 无下一页')
#
#     def parse_post_url(self, response):
#
#         self.logger.debug('文章parse---')
#         category_path = response.xpath('//body/div[@class="tableborder2"][1]')
#         category_title = category_path.xpath('./a[3]/text()')[0].extract()
#         self.logger.debug('文章parse 栏目: %s' % category_title)
#
#         for res in response.xpath('//body/div[contains(@class, "postlary")]'):
#             try:
#                 user_info_path = res.xpath('./div[contains(@class, "postuserinfo")]')
#                 user_id = user_info_path.xpath('./div[1]/div[1]/font/b/text()').extract()[0]
#                 atlas_name = category_title + '_' + user_id
#                 if atlas_name in user_list:
#                     continue
#
#                 user_item = UserItem()
#                 user_item['userid'] = user_id
#
#                 # 如果redis中已存在, 则忽略
#                 if redis_client.set_in(user_id):
#                     continue
#
#                 category_user_item = CategoryUserItem()
#                 category_user_item['category_name'] = category_title
#                 category_user_item['userid'] = user_id
#
#                 child_res = user_info_path.xpath('./div[3]/following-sibling::div')
#                 for child in child_res:
#                     _type = child.xpath('./text()').extract()[0].strip()
#                     if _type.startswith('交易等级'):
#                         trade_level = re.split(r'[:：]', _type)[1]
#                         user_item['trade_level'] = trade_level
#                         self.logger.debug('trade_level URL %s %s' % (response.url, trade_level))
#                     elif _type.startswith('信用积分'):
#                         credit_score = re.split(r'[:：]', _type)[1]
#                         user_item['credit_score'] = credit_score
#                         self.logger.debug('credit_score URL %s %s' % (response.url, credit_score))
#                     elif _type.startswith('评分次数'):
#                         score_count = re.split(r'[:：]', _type)[1]
#                         user_item['score_count'] = score_count
#                         self.logger.debug('score_count URL %s %s' % (response.url, score_count))
#                     elif _type.startswith('发贴次数'):
#                         post_count = re.split(r'[:：]', _type)[1]
#                         user_item['post_count'] = post_count
#                         self.logger.debug('post_count URL %s %s' % (response.url, post_count))
#                     elif _type.startswith('发帖积分'):
#                         post_score = re.split(r'[:：]', _type)[1]
#                         user_item['post_score'] = post_score
#                         self.logger.debug('post_score URL %s %s' % (response.url, post_score))
#                     elif _type.startswith('注册日期'):
#                         register_time = re.split(r'[:：]', _type)[1]
#                         user_item['register_time'] = register_time
#                         self.logger.debug('register_time URL %s %s' % (response.url, register_time))
#
#                 post_info_path = res.xpath('./div[@class="post"]')
#
#                 user_detail = post_info_path.xpath('./div[last()]')[-1].xpath('./text()').extract()
#                 if user_detail[-1] == '\r\n' or user_detail[-1].endswith('个金币'):
#                     user_detail = post_info_path.xpath('./div[last()-1]').extract()
#
#                 self.logger.debug('信息 %s' % user_detail[1:])
#                 for content in user_detail[1:]:
#                     content = content.strip()
#                     if content.startswith('认证员注') and 'remark' not in user_item:
#                         remark = re.split(r'[:：]', content)[-1]
#                         user_item['remark'] = remark
#                         self.logger.debug('remark URL %s %s' % (response.url, remark))
#
#                     elif ('姓名' in content or '姓 名' in content or '姓&nbsp;&nbsp;名' in content or '姓\xa0\xa0\xa0\xa0名'
#                           in content) \
#                             and 'name' not in user_item:
#                         name = re.split(r'[(（]', re.split(r'[:：]', content)[-1])[0]
#                         user_item['name'] = name
#                         self.logger.debug('name URL %s %s' % (response.url, name))
#
#                     elif ('地址' in content or '地 址' in content or '速递' in content) and 'address' not in user_item:
#                         if ':' or '：' in content:
#                             address = re.split(r'[:：]', content)[1]
#                         elif '\xa0\xa0' in content:
#                             address = re.split(r'[\xa0\xa0]', content)[1]
#                         else:
#                             address = re.split(r'[ ]', content)[1]
#                         user_item['address'] = address
#                         self.logger.debug('address URL %s %s' % (response.url, address))
#
#                     elif '电话' in content or '手机' in content or '手 机' in content or '电 话' in content:
#                         user_phone1, user_phone2 = search_phone(content)
#                         user_fix_phone = search_fix_phone(content)
#                         if 'fixed_phone' not in user_item:
#                             user_item['fixed_phone'] = user_fix_phone if user_fix_phone is not None else ''
#                             self.logger.debug('fixed_phone URL %s %s' % (response.url, user_fix_phone))
#                         if 'phone_1' not in user_item:
#                             user_item['phone_1'] = user_phone1 if user_phone1 is not None else ''
#                             self.logger.debug('phone_1 URL %s %s' % (response.url, user_phone1))
#                         if 'phone_2' not in user_item:
#                             user_item['phone_2'] = user_phone2 if user_phone2 is not None else ''
#                             self.logger.debug('phone_2 URL %s %s' % (response.url, user_phone2))
#
#                 user_list.append(atlas_name)
#
#                 self.logger.debug('文章parse 文章URl %s 用户信息 %s' % (response.url, user_item))
#
#                 yield category_user_item
#                 yield user_item
#             except Exception as e:
#                 self.logger.error('文章parse失败 %s %s' % (e, response.url), exc_info=True)
#
#         page_links = response.xpath('/html/body/div[@class="mainbar0"]/div[1]/table[1]/form[1]/tr/td')
#         cur_index = 1
#         # 找到当前页
#         for index, link in enumerate(page_links):
#             current_link = link.xpath('./font')
#             if current_link:
#                 cur_index = index
#                 break
#         next_link = page_links[cur_index + 1]
#         # 判断下一个元素 是否是下一页
#         next_pages = next_link.xpath('./a/@href')
#         if next_pages:
#             next_page = SITE_URL + '/' + next_pages[0].extract()
#             # next_page = urljoin(SITE_URL, next_pages[0].extract())
#             self.logger.debug('文章parse 下一页 %s' % next_page)
#             print('POST下一页', next_page)
#             yield scrapy.Request(next_page, callback=self.parse_post_url)
#         else:
#             self.logger.debug('文章parse 无下一页')
#  def parse_post_url(self, response):
#
#         self.logger.debug('文章parse---')
#         category_path = response.xpath('//body/div[@class="tableborder2"][1]')
#         category_title = category_path.xpath('./a[3]/text()')[0].extract()
#         self.logger.debug('文章parse 栏目: %s' % category_title)
#
#         for res in response.xpath('//body/div[contains(@class, "postlary")]'):
#             try:
#                 user_info_path = res.xpath('./div[contains(@class, "postuserinfo")]')
#                 user_id = user_info_path.xpath('./div[1]/div[1]/font/b/text()').extract()[0]
#                 atlas_name = category_title + '_' + user_id
#                 if atlas_name in user_list:
#                     continue
#
#                 user_item = UserItem()
#                 user_item['userid'] = user_id
#
#                 # 如果redis中已存在, 则忽略
#                 if redis_client.set_in(user_id):
#                     continue
#
#                 category_user_item = CategoryUserItem()
#                 category_user_item['category_name'] = category_title
#                 category_user_item['userid'] = user_id
#
#                 child_res = user_info_path.xpath('./div[3]/following-sibling::div')
#                 for child in child_res:
#                     _type = child.xpath('./text()').extract()[0].strip()
#                     if _type.startswith('交易等级'):
#                         trade_level = re.split(r'[:：]', _type)[1]
#                         user_item['trade_level'] = trade_level
#                         self.logger.debug('trade_level URL %s %s' % (response.url, trade_level))
#                     elif _type.startswith('信用积分'):
#                         credit_score = re.split(r'[:：]', _type)[1]
#                         user_item['credit_score'] = credit_score
#                         self.logger.debug('credit_score URL %s %s' % (response.url, credit_score))
#                     elif _type.startswith('评分次数'):
#                         score_count = re.split(r'[:：]', _type)[1]
#                         user_item['score_count'] = score_count
#                         self.logger.debug('score_count URL %s %s' % (response.url, score_count))
#                     elif _type.startswith('发贴次数'):
#                         post_count = re.split(r'[:：]', _type)[1]
#                         user_item['post_count'] = post_count
#                         self.logger.debug('post_count URL %s %s' % (response.url, post_count))
#                     elif _type.startswith('发帖积分'):
#                         post_score = re.split(r'[:：]', _type)[1]
#                         user_item['post_score'] = post_score
#                         self.logger.debug('post_score URL %s %s' % (response.url, post_score))
#                     elif _type.startswith('注册日期'):
#                         register_time = re.split(r'[:：]', _type)[1]
#                         user_item['register_time'] = register_time
#                         self.logger.debug('register_time URL %s %s' % (response.url, register_time))
#
#                 post_info_path = res.xpath('./div[@class="post"]')
#
#                 user_detail = post_info_path.xpath('./div[last()]')[-1].xpath('./text()').extract()
#                 if user_detail[-1] == '\r\n' or user_detail[-1].endswith('个金币'):
#                     user_detail = post_info_path.xpath('./div[last()-1]').extract()
#
#                 self.logger.debug('信息 %s' % user_detail[1:])
#                 for content in user_detail[1:]:
#                     content = content.strip()
#                     if content.startswith('认证员注') and 'remark' not in user_item:
#                         remark = re.split(r'[:：]', content)[-1]
#                         user_item['remark'] = remark
#                         self.logger.debug('remark URL %s %s' % (response.url, remark))
#
#                     elif ('姓名' in content or '姓 名' in content or '姓&nbsp;&nbsp;名' in content or '姓\xa0\xa0\xa0\xa0名'
#                           in content) \
#                             and 'name' not in user_item:
#                         name = re.split(r'[(（]', re.split(r'[:：]', content)[-1])[0]
#                         user_item['name'] = name
#                         self.logger.debug('name URL %s %s' % (response.url, name))
#
#                     elif ('地址' in content or '地 址' in content or '速递' in content) and 'address' not in user_item:
#                         if ':' or '：' in content:
#                             address = re.split(r'[:：]', content)[1]
#                         elif '\xa0\xa0' in content:
#                             address = re.split(r'[\xa0\xa0]', content)[1]
#                         else:
#                             address = re.split(r'[ ]', content)[1]
#                         user_item['address'] = address
#                         self.logger.debug('address URL %s %s' % (response.url, address))
#
#                     elif '电话' in content or '手机' in content or '手 机' in content or '电 话' in content:
#                         user_phone1, user_phone2 = search_phone(content)
#                         user_fix_phone = search_fix_phone(content)
#                         if 'fixed_phone' not in user_item:
#                             user_item['fixed_phone'] = user_fix_phone if user_fix_phone is not None else ''
#                             self.logger.debug('fixed_phone URL %s %s' % (response.url, user_fix_phone))
#                         if 'phone_1' not in user_item:
#                             user_item['phone_1'] = user_phone1 if user_phone1 is not None else ''
#                             self.logger.debug('phone_1 URL %s %s' % (response.url, user_phone1))
#                         if 'phone_2' not in user_item:
#                             user_item['phone_2'] = user_phone2 if user_phone2 is not None else ''
#                             self.logger.debug('phone_2 URL %s %s' % (response.url, user_phone2))
#
#                 user_list.append(atlas_name)
#
#                 self.logger.debug('文章parse 文章URl %s 用户信息 %s' % (response.url, user_item))
#
#                 yield category_user_item
#                 yield user_item
#             except Exception as e:
#                 self.logger.error('文章parse失败 %s %s' % (e, response.url), exc_info=True)
#
#         page_links = response.xpath('/html/body/div[@class="mainbar0"]/div[1]/table[1]/form[1]/tr/td')
#         cur_index = 1
#         # 找到当前页
#         for index, link in enumerate(page_links):
#             current_link = link.xpath('./font')
#             if current_link:
#                 cur_index = index
#                 break
#         next_link = page_links[cur_index + 1]
#         # 判断下一个元素 是否是下一页
#         next_pages = next_link.xpath('./a/@href')
#         if next_pages:
#             next_page = SITE_URL + '/' + next_pages[0].extract()
#             # next_page = urljoin(SITE_URL, next_pages[0].extract())
#             self.logger.debug('文章parse 下一页 %s' % next_page)
#             print('POST下一页', next_page)
#             yield scrapy.Request(next_page, callback=self.parse_post_url)
#         else:
#             self.logger.debug('文章parse 无下一页')


class SlaveSpider(RedisSpider):
    name = "kc_slave"
    redis_key = "kc0011_slave:start_urls"

    # handle_httpstatus_list = [404, 200]

    def parse(self, response):
        self.logger.debug('文章parse---')
        category_path = response.xpath('//body/div[@class="tableborder2"][1]')
        if len(category_path.xpath('./a')) == 3:
            category_title = category_path.xpath('./a[2]/text()')[0].extract()
        else:
            category_title = category_path.xpath('./a[3]/text()')[0].extract()

        self.logger.debug('文章parse 栏目: %s' % category_title)

        for res in response.xpath('//body/div[contains(@class, "postlary")]'):
            try:
                user_info_path = res.xpath('./div[contains(@class, "postuserinfo")]')
                user_id = user_info_path.xpath('./div[1]/div[1]/font/b/text()').extract()[0]
                atlas_name = category_title + '_' + user_id

                user_item = UserItem()
                user_item['userid'] = user_id

                # 如果redis中已存在, 则忽略
                if redis_client.set_in(user_id):
                    continue

                category_user_item = CategoryUserItem()
                category_user_item['category_name'] = category_title
                category_user_item['userid'] = user_id

                child_res = user_info_path.xpath('./div[3]/following-sibling::div')
                for child in child_res:
                    _type = child.xpath('./text()').extract()[0].strip()
                    if _type.startswith('交易等级'):
                        trade_level = re.split(r'[:：]', _type)[1]
                        user_item['trade_level'] = trade_level
                        self.logger.debug('trade_level URL %s %s' % (response.url, trade_level))
                    elif _type.startswith('信用积分'):
                        credit_score = re.split(r'[:：]', _type)[1]
                        user_item['credit_score'] = credit_score
                        self.logger.debug('credit_score URL %s %s' % (response.url, credit_score))
                    elif _type.startswith('评分次数'):
                        score_count = re.split(r'[:：]', _type)[1]
                        user_item['score_count'] = score_count
                        self.logger.debug('score_count URL %s %s' % (response.url, score_count))
                    elif _type.startswith('发贴次数'):
                        post_count = re.split(r'[:：]', _type)[1]
                        user_item['post_count'] = post_count
                        self.logger.debug('post_count URL %s %s' % (response.url, post_count))
                    elif _type.startswith('发帖积分'):
                        post_score = re.split(r'[:：]', _type)[1]
                        user_item['post_score'] = post_score
                        self.logger.debug('post_score URL %s %s' % (response.url, post_score))
                    elif _type.startswith('注册日期'):
                        register_time = re.split(r'[:：]', _type)[1]
                        user_item['register_time'] = register_time
                        self.logger.debug('register_time URL %s %s' % (response.url, register_time))

                post_info_path = res.xpath('./div[@class="post"]')

                user_detail = post_info_path.xpath('./div[last()]')[-1].xpath('./text()').extract()
                if user_detail[-1] == '\r\n' or user_detail[-1].endswith('个金币'):
                    user_detail = post_info_path.xpath('./div[last()-1]').extract()

                self.logger.debug('信息 %s' % user_detail[1:])
                for content in user_detail[1:]:
                    content = content.strip()
                    if content.startswith('认证员注') and 'remark' not in user_item:
                        remark = re.split(r'[:：]', content)[-1]
                        user_item['remark'] = remark
                        self.logger.debug('remark URL %s %s' % (response.url, remark))

                    elif ('姓名' in content or '姓 名' in content or '姓&nbsp;&nbsp;名' in content or '姓\xa0\xa0\xa0\xa0名'
                          in content) \
                            and 'name' not in user_item:
                        name = re.split(r'[(（]', re.split(r'[:：]', content)[-1])[0]
                        user_item['name'] = name
                        self.logger.debug('name URL %s %s' % (response.url, name))

                    elif ('地址' in content or '地 址' in content or '速递' in content) and 'address' not in user_item:
                        if ':' or '：' in content:
                            address = re.split(r'[:：]', content)[1]
                        elif '\xa0\xa0' in content:
                            address = re.split(r'[\xa0\xa0]', content)[1]
                        else:
                            address = re.split(r'[ ]', content)[1]
                        user_item['address'] = address
                        self.logger.debug('address URL %s %s' % (response.url, address))

                    elif '电话' in content or '手机' in content or '手 机' in content or '电 话' in content:
                        user_phone1, user_phone2 = search_phone(content)
                        user_fix_phone = search_fix_phone(content)
                        if 'fixed_phone' not in user_item:
                            user_item['fixed_phone'] = user_fix_phone if user_fix_phone is not None else ''
                            self.logger.debug('fixed_phone URL %s %s' % (response.url, user_fix_phone))
                        if 'phone_1' not in user_item:
                            user_item['phone_1'] = user_phone1 if user_phone1 is not None else ''
                            self.logger.debug('phone_1 URL %s %s' % (response.url, user_phone1))
                        if 'phone_2' not in user_item:
                            user_item['phone_2'] = user_phone2 if user_phone2 is not None else ''
                            self.logger.debug('phone_2 URL %s %s' % (response.url, user_phone2))

                self.logger.debug('文章parse 文章URl %s 用户信息 %s' % (response.url, user_item))

                yield category_user_item
                yield user_item
            except Exception as e:
                self.logger.error('文章parse失败 %s %s' % (e, response.url), exc_info=True)

        page_links = response.xpath('/html/body/div[@class="mainbar0"]/div[1]/table[1]/form[1]/tr/td')
        cur_index = 1
        # 找到当前页
        for index, link in enumerate(page_links):
            current_link = link.xpath('./font')
            if current_link:
                cur_index = index
                break
        next_link = page_links[cur_index + 1]
        # 判断下一个元素 是否是下一页
        next_pages = next_link.xpath('./a/@href')
        if next_pages:
            next_page = SITE_URL + '/' + next_pages[0].extract()
            # next_page = urljoin(SITE_URL, next_pages[0].extract())
            self.logger.debug('文章parse 下一页 %s' % next_page)
            print('POST下一页', next_page)
            yield scrapy.Request(next_page, callback=self.parse)
        else:
            self.logger.debug('文章parse 无下一页')










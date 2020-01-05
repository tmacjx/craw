"""
# @Author  wk
# @Time 2019/12/29 21:42

"""

# coding: utf-8
from scrapy import Item, Field
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider, RedisSpider
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin
from utils import redis_client
import scrapy
import urllib.parse as urlparse


SITE_URL = "http://www.kc0011.net"
IGNORE_TITLE = ('投诉暴光台', '交易视点', '中介支付专栏')


class LinkItem(Item):
    name = Field()
    link = Field()


class MasterSpider(RedisCrawlSpider):
    name = 'kc_master'
    redis_key = 'kc:start_urls'
    start_urls = [
        'http://kc0011.net/index.asp',
        ]
    # kc_main_lx = LinkExtractor(deny=(r'http://kc0011.net/index.asp', ))
    kc_category2_lx = LinkExtractor(allow=(r'http://www.kc0011.net/\?boardid=\d+',
                                           r'http://kc0011.net/index.asp\?boardid=\d+'),
                                    # deny=(r'http://www.kc0011.net/index.asp\?boardid=16',
                                    #       r'http://www.kc0011.net/index.asp\?boardid=17',
                                    #       r'http://www.kc0011.net/index.asp\?boardid=19',
                                    # ),
                                    )

    rules = (
        Rule(kc_category2_lx, callback='parse_category', follow=False),
    )

    def __init__(self, *args, **kwargs):
        # domain = kwargs.pop('domain', '')
        # self.allowed_domains = filter(None, domain.split(','))
        super(MasterSpider, self).__init__(*args, **kwargs)

    # def parse(self, response):
    #     self.logger.debug('主页parse---')
    #     for sel in response.xpath('//body/div[contains(@class, "mainbar")][last()-6]'):
    #         title_sel = sel.xpath('./div/div[last()-1]')[1].xpath('./a')
    #         title = title_sel.xpath('./text()').extract()[0]
    #         self.logger.debug('主页parse 栏目: %s' % title)
    #         category_pages = title_sel.xpath('./@href')
    #         if category_pages:
    #
    #             category_page = urljoin(SITE_URL, category_pages[0].extract())
    #             self.logger.debug('主页parse 栏目URL: %s' % category_pages)
    #             item = LinkItem()
    #             item['name'] = title
    #             item['link'] = category_page
    #             yield scrapy.Request(item['link'], callback=self.parse_category)
    #
    #     for sel in response.xpath('//body/div[contains(@class, "mainbar")][last()-8]'):
    #         title_sel = sel.xpath('./div/div[last()-1]')[1].xpath('./a')
    #         title = title_sel.xpath('./text()').extract()[0]
    #         self.logger.debug('主页parse 栏目: %s' % title)
    #         category_pages = title_sel.xpath('./@href')
    #         if category_pages:
    #             category_page = urljoin(SITE_URL, category_pages[0].extract())
    #             self.logger.debug('主页parse 栏目URL: %s' % category_pages)
    #             item = LinkItem()
    #             item['name'] = title
    #             item['link'] = category_page
    #             yield scrapy.Request(item['link'], callback=self.parse_category)
    #
    #     for sel in response.xpath('//body/div[contains(@class, "mainbar") and contains(@style,"height:60px") '
    #                               'and contains(@style,"line-height:18px")]'):
    #         category_title = sel.xpath('./div/div/a')
    #         for title_sel in category_title:
    #             title = title_sel.xpath('./text()').extract()[0]
    #             if title in IGNORE_TITLE:
    #                 continue
    #             self.logger.debug('主页parse 栏目: %s' % title)
    #             category_pages = title_sel.xpath('./@href')
    #             if category_pages:
    #                 category_page = urljoin(SITE_URL, category_pages[0].extract())
    #                 self.logger.debug('主页parse 栏目URL: %s' % category_pages)
    #                 item = LinkItem()
    #                 item['name'] = title
    #                 item['link'] = category_page
    #                 yield scrapy.Request(item['link'], callback=self.parse_category)

    def parse_category(self, response):
        self.logger.debug('栏目parse---')
        for post_sel in response.xpath('/html/body/form[1]/div[@class="list"]/div[@class="listtitle"]/a'):
            post_pages = post_sel.xpath('./@href')
            if post_pages:
                post_page = SITE_URL + '/' + post_pages[0].extract()
                self.logger.debug('栏目parse 文章URL: %s' % post_page)
                try:
                    # salve lpush
                    self._filter_url(post_page)
                except Exception as e:
                    print(e)

        page_links = response.xpath('/html/body/div[@class="mainbar0"][last()-1]/div[1]/table[1]/form[1]/tr/td')
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
            next_url = SITE_URL + '/' + next_pages[0].extract()
            parsed = urlparse.urlparse(next_url)
            querys = urlparse.parse_qs(parsed.query)
            querys = {k: v[0] for k, v in querys.items()}
            page = querys.get('page')
            if 'boardid' in querys:
                board_id = querys.get('boardid')
            else:
                board_id = querys.get('boardID')
            next_page = SITE_URL + '/?' + 'boardID=' + board_id + '&page=' + page
            # next_page = urljoin(SITE_URL, next_pages[0].extract())
            self.logger.debug('栏目parse 下一页: %s' % next_page)
            yield self.make_requests_from_url(next_page)
        else:
            self.logger.debug('栏目parse 无下一页')

    def _filter_url(self, url, key="kc0011_slave:start_urls"):
        is_new_url = bool(redis_client.pfadd(key + "_filter", url))
        if is_new_url:
            res = redis_client.lpush(key, url)
            self.logger.debug('salve url add %s' % res)

    # def _build_url(self, url):
    #     parse = urlparse(url)
    #     query = parse_qs(parse.query)
    #     base = parse.scheme + '://' + parse.netloc + parse.path
    #
    #     if '_ipg' not in query.keys() or '_pgn' not in query.keys() or '_skc' in query.keys():
    #         new_url = base + "?" + urlencode({"_ipg": "200", "_pgn": "1"})
    #     else:
    #         new_url = base + "?" + urlencode({"_ipg": query['_ipg'][0], "_pgn": int(query['_pgn'][0]) + 1})
    #     return new_url




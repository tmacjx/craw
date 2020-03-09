"""
# @Author  wk
# @Time 2019/12/29 21:42

"""

from scrapy import Item, Field
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.linkextractors import LinkExtractor
from craw.utils import redis_client
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
        super(MasterSpider, self).__init__(*args, **kwargs)

    def parse_category(self, response):
        category_path = response.xpath('//body/div[@class="tableborder2"][1]')
        if len(category_path.xpath('./a')) == 3:
            category_title = category_path.xpath('./a[2]/text()')[0].extract()
        else:
            category_title = category_path.xpath('./a[3]/text()')[0].extract()

        self.logger.debug('文章parse 栏目: %s %s' % (category_title, response.url))

        post_len = len(response.xpath('/html/body/form[1]/div[@class="list"]/div[@class="listtitle"]/a'))
        if post_len == 0:
            self.logger.debug("无post_len %s %s" % (category_title, response.url))
            return

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
        if len(page_links) == 0:
            x = response.xpath('/html/body').extract()
            self.logger.debug('body')
            self.logger.debug(x)
        cur_index = 1
        # 找到当前页
        for index, link in enumerate(page_links):
            current_link = link.xpath('./font')
            if current_link:
                cur_index = index
                break

        next_link = page_links[cur_index + 1]
        self.logger.debug('栏目parse 当前页 %s' % response.url)
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
        # is_new_url = bool(redis_client.pfadd(key + "_filter", url))
        # if is_new_url:
        is_exist = redis_client.set_member(url, key='url_set')
        if not bool(is_exist):
            redis_client.set_add(url, key="url_set")
            res = redis_client.lpush(key, url)
            self.logger.debug('salve url add %s' % res)




# -*- coding: utf-8 -*-

# Scrapy settings for craw project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'craw'

SPIDER_MODULES = ['craw.spiders']
NEWSPIDER_MODULE = 'craw.spiders'


LOG_FILE = "craw.log"
LOG_LEVEL = "DEBUG"
RETRY_TIMES = 10
DOWNLOAD_TIMEOUT = 60
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'craw (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

SQLITE_DB_NAME = 'sqlite3.db'

ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 300,
    'craw.pipelines.MysqlPipeline': 400,
    # 'craw.pipelines.SQLitePipeline': 400,
}


MYSQL_HOST = "47.100.89.250"
MYSQL_DATABASE = 'bbs'
MYSQL_USER = 'class'
MYSQL_PASSWORD = 'mypwd'
MYSQL_PORT = 3306
# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.5
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'craw.middlewares.CrawSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'craw.middlewares.CrawDownloaderMiddleware': 543,
# }
#
DOWNLOADER_MIDDLEWARES = {
    'craw.middlewares.RandomUserAgent': 543,
    'craw.middlewares.ProxyMiddleware': 643,
    # 'craw.middlewares.ProxyStaticMiddleware': 643,
}


# 114.104.182.71:49476
# 183.166.119.13:48719
# 180.124.36.67:20845
# 222.185.223.173:29908
# 222.185.223.235:41551
# 27.157.58.124:36751
# 121.226.57.143:34472
# 118.120.184.182:29437
# 60.169.124.183:43522
# 123.163.21.191:33917
# 123.163.132.174:26066
# 27.152.194.29:37758
# 180.110.151.18:29359
# 106.110.195.231:20473
# 113.221.46.8:42383
# 106.111.222.28:49557
# 218.73.47.215:20470
# 171.9.116.161:31750
# 125.112.38.143:25916
# 122.241.28.49:36243

PROXIES = [
    'http://125.122.19.196:22454',
    'http://125.119.181.80:44656'
]

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'craw.pipelines.CrawPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# 启用Redis调度存储请求队列
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# 确保所有的爬虫通过Redis去重
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"


# 不清除Redis队列、这样可以暂停/恢复 爬取
SCHEDULER_PERSIST = True


#指定连接到redis时使用的端口和地址（可选）
# REDIS_HOST = 'localhost'
# REDIS_PORT = 6379


REDIS_URL = 'redis://:123456@47.100.89.250:6379'  # for master

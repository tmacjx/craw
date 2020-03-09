scrapy

scrapy-redis

mysql

redis

### 分布式爬取某文玩论坛
运行master采集网页
> nohup python run_master.py & >/dev/null

运行slave解析网页
> nohup python run_salve.py & >/dev/null

总结
1.机器低配时设置 HTTPCACHE_ENABLED=False, 避免linux inode耗尽

2.scrapy-redis salve启动时消费redis的list
但是同时默认启动了Item会记录每次处理的页面信息，造成redis内存不降反增
  

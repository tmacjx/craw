### 分布式爬取某文玩论坛
scrapy

scrapy-redis

mysql

redis


运行master采集网页
> nohup python run_master.py & >/dev/null

运行slave解析网页
> nohup python run_salve.py & >/dev/null

总结

1.机器低配时设置HTTPCACHE_ENABLED=False, 避免linux inode耗尽

2.salve启动时消费master生产的redis list
但是同时默认启动了ItemPipeline会记录每次处理的页面信息，造成redis内存不降反增

3.网页URL可以md5处理, 作为去重判断
  

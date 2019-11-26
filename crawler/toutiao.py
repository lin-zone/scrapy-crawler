# -*- coding: utf-8 -*-
"""
    输入关键词爬取头条新闻
    运行: python toutiao.py [keyword]
    使用Chrome浏览器访问 https://www.toutiao.com/search/ 输入关键词
    按F12调试 -> Network -> XHR, 下拉页面, 看到不断加载的XHR文件
    链接示例: https://www.toutiao.com/api/search/content/?aid=24&app_name=web_search&offset=20&format=json&keyword=python&autoload=true&count=20&en_qc=1&cur_tab=1&from=search_tab&pd=synthesis&timestamp=1574731888828
    Scrapy API: FormRequest, DownloaderMiddler
    需要保存网站设置的cookies, 否则请求的数据错误
    使用Selenium驱动从Firefox浏览器中获取cookies值并设置为爬虫的cookies
    使用response.headers.getlist('Set-Cookie')获得的cookies值不准确
"""
import json
from itertools import count

import scrapy
from scrapy.crawler import CrawlerProcess


class ToutiaoItem(scrapy.Item):
    title = scrapy.Field()              # 文章标题
    source = scrapy.Field()             # 文章来源
    abstract = scrapy.Field()           # 文章简介
    datetime = scrapy.Field()           # 发表日期
    article_url = scrapy.Field()        # 文章链接
    comment_count = scrapy.Field()      # 评论人数


class TouotiaoSpider(scrapy.Spider):
    name = 'touotiao'
    allowed_domains = ['www.toutiao.com']
    base_url = 'https://www.toutiao.com/api/search/content/'
    offset = count(0, 20)

    def __init__(self, keyword):
        self.keyword = keyword

    def start_requests(self):
        yield self.get_page()

    def get_page(self):
        offset = next(self.offset)
        formdata  = {
            'aid': '24',
            'app_name': 'web_search',
            'offset': str(offset),
            'format': 'json',
            'keyword': self.keyword,
            'autoload': 'true',
            'count': '20',
            'en_qc': '1',
            'cur_tab': '1',
            'from': 'search_tab',
            'pd': 'synthesis',
        }
        return scrapy.FormRequest(self.base_url, method='GET', formdata=formdata)

    def parse(self, response):
        js = json.loads(response.text)
        if not js.get('count'):         # 如果没有数据, 结束爬虫
            return
        for d in js['data']:
            item = ToutiaoItem()
            for field in item.fields:
                item[field] = d.get(field)
            print(item['title'])
            yield item
        yield self.get_page()           # 下一页


DOWNLOADER_MIDDLEWARES = {
   'utils.middlewares.UserAgentMiddleware': 543,
   'utils.middlewares.FirefoxSetCookiesMiddleware': 544,
}
settings = dict(
    LOG_ENABLED=False,
    FEED_URI = 'toutiao.json',                          # 导出文件路径
    FEED_FORMAT = 'json',                               # 导出数据格式
    FEED_EXPORT_ENCODING = 'UTF8',                      # 导出文件编码
    DOWNLOADER_MIDDLEWARES=DOWNLOADER_MIDDLEWARES,
)


if __name__ == "__main__":
    import sys

    keyword = sys.argv[1]
    process = CrawlerProcess(settings=settings)
    process.crawl(TouotiaoSpider, keyword=keyword)
    process.start()
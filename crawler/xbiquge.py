# -*- coding: utf-8 -*-
"""
    爬取笔趣阁小说并写入txt文件
    全部小说: http://www.xbiquge.la/xiaoshuodaquan/
    运行: python xbiquge.py [url]
    例如: python xbiquge.py http://www.xbiquge.la/15/15409/
    默认将小说下载在novels文件夹中, 修改settings的NOVELS_STORE变量可以更改保存文件夹
"""
import os
from operator import itemgetter

import scrapy
from scrapy.crawler import CrawlerProcess


class XbiqugeSpider(scrapy.Spider):
    name = 'xbiquge'
    allowed_domains = ['www.xbiquge.la']
    novel_info = {}

    def __init__(self, url):
        self.start_urls = [url]

    def parse(self, response):
        q = response.css
        self.novel_info['bookname'] = q('#info h1::text').get()
        print(self.novel_info['bookname'])
        self.novel_info['author'] = q('#info p::text').get().split('：')[-1]
        selectors = q('#list a')
        for index, selector in enumerate(selectors, 1):
            yield response.follow(
                selector,
                callback=self.parse_item,
                meta=dict(index=index),
            )
    
    def parse_item(self, response):
        q =response.css
        item = {}
        item['index'] = response.meta['index']
        item['title'] = q('.bookname h1::text').get()
        item['content'] = ''.join(q('#content::text').getall())
        print(item['title'])
        yield item


class TxtPipeline(object):

    def open_spider(self, spider):
        self.novel_info = spider.novel_info
        self.data = []

    def process_item(self, item, spider):
        self.data.append(dict(item))
        return item

    def close_spider(self, spider):
        # 将data里的数据排序然后写入txt文件
        bookname = self.novel_info['bookname']
        author = self.novel_info['author']
        path = self.get_path(spider)
        self.data.sort(key=itemgetter('index')) # 按索引排序
        with open(path, 'a', encoding='UTF8') as f:
            f.write(f'{bookname} - {author}\n\n')
            for item in self.data:
                title = item['title']
                content = item['content']
                f.write(f'{title}\n\n')
                f.write(f'{content}\n\n')

    def get_path(self, spider):
        # 从settings里读取小说保存文件夹路径, 如果文件夹不存在, 创建
        # 然后返回小说保存路径, 文件名为小说名
        folder = spider.settings['NOVELS_STORE']
        if not os.path.isdir(folder):
            os.mkdir(folder)
        bookname = self.novel_info['bookname']
        path = os.path.join(folder, f'{bookname}.txt')
        return path


ITEM_PIPELINES = {
    'xbiquge.TxtPipeline': 300,
}
settings = dict(
    LOG_ENABLED=False,
    ITEM_PIPELINES=ITEM_PIPELINES,
    NOVELS_STORE='novels',
)


if __name__ == "__main__":
    import sys

    url = sys.argv[1]
    process = CrawlerProcess(settings=settings)
    process.crawl(XbiqugeSpider, url=url)
    process.start()
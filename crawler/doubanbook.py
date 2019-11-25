# -*- coding: utf-8 -*-
"""
    根据图书标签爬取豆瓣图书
    eg: https://book.douban.com/tag/python?start=20&type=T
    所有标签: https://book.douban.com/tag/
    Scrapy API: ItemLoader, DownloadMiddleware, Feed Export
"""
from itertools import count

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Compose
from scrapy.crawler import CrawlerProcess


class BookItem(scrapy.Item):
    title = scrapy.Field()              # 图书标题
    link = scrapy.Field()               # 豆瓣链接
    pub = scrapy.Field()                # 出版信息
    comment_count = scrapy.Field()      # 评价人数
    intro = scrapy.Field()              # 图书简介
    price = scrapy.Field()              # 图书价格
    image_urls = scrapy.Field()         # 封面链接


class BookLoader(ItemLoader):
    default_item_class = BookItem
    default_output_processor = Compose(TakeFirst(), str.strip)


class DoubanbookSpider(scrapy.Spider):
    name = 'doubanbook'
    allowed_domains = ['book.douban.com']
    base_url = 'https://book.douban.com/tag/{tag}?start={offset}&type={sort_id}'

    def __init__(self, tags, sort_id='T'):
        self.tags = iter(tags)
        # 综合排序: T, 按出版日期排序: R, 按评价排序: S
        self.sort_id = sort_id

    def next_tag(self):
        """从图书标签生成器中获取下一个标签并将偏移量重置,如果标签拿完关闭爬虫"""
        try:
            self.tag = next(self.tags)
        except StopIteration:
            raise scrapy.exceptions.CloseSpider("no tag")
        self.offset = count(0, 20)      # 偏移量从0开始增长, 增长量为20(每一页有20本书)

    def get_page(self):
        """返回Request对象"""   
        url = self.base_url.format(
            tag=self.tag,
            offset=str(next(self.offset)),
            sort_id=self.sort_id,
        )
        return scrapy.Request(url, callback=self.parse)      

    def start_requests(self):
        self.next_tag()
        yield self.get_page()

    def parse(self, response):
        books = response.css('.subject-item')
        if not books:           # 如果页面中无图书列表,继续下一图书标签的爬取
            self.next_tag()
        for book in books:      # 提取图书信息
            l = BookLoader(selector=book)
            l.add_css('title', 'h2 a::attr(title)')
            l.add_css('link', 'h2 a::attr(href)')
            l.add_css('pub', '.pub::text')
            l.add_css('comment_count', '.pl::text')
            l.add_css('intro', '.info p::text')
            l.add_css('price', '.buy-info a::text')
            l.add_css('image_urls', '.pic img::attr(src)')
            item = l.load_item()
            print(item['title'])
            yield item
        yield self.get_page()   # 爬取下一页


DOWNLOADER_MIDDLEWARES = {
   'utils.middlewares.UserAgentDownloadMiddleware': 543,
}
settings = dict(
    LOG_ENABLED=False,
    FEED_URI = 'books.json',                            # 导出文件路径
    FEED_FORMAT = 'json',                               # 导出数据格式
    FEED_EXPORT_ENCODING = 'UTF8',                      # 导出文件编码
    DOWNLOADER_MIDDLEWARES=DOWNLOADER_MIDDLEWARES,
)


if __name__ == "__main__":
    # test input:
    # tags: flask,django,scrapy,mongodb
    tags = input('tags:').split(',')
    process = CrawlerProcess(settings=settings)
    process.crawl(DoubanbookSpider, tags=tags)
    process.start()
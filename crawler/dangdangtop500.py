# -*- coding: utf-8 -*-
"""
    爬取当当网 Top 500 本五星好评书籍
    链接: http://bang.dangdang.com/books/fivestars/01.00.00.00.00.00-recent30-0-0-1-1
    Scrapy API: ItemLoader, DownloadMiddleware, Feed Export
    设置 User-Agent
"""
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.crawler import CrawlerProcess


class BookItem(scrapy.Item):
    image_url = scrapy.Field()      # 封面链接
    title = scrapy.Field()          # 图书标题
    link = scrapy.Field()           # 图书链接
    author = scrapy.Field()         # 作者信息
    pub_date = scrapy.Field()       # 出版日期
    publisher = scrapy.Field()      # 出版社
    price_n = scrapy.Field()        # 现价
    price_r = scrapy.Field()        # 原价
    price_s = scrapy.Field()        # 折扣


class BookLoader(ItemLoader):
    default_item_class = BookItem
    default_output_processor = TakeFirst()


class Dangdangtop500Spider(scrapy.Spider):
    name = 'dangdangtop500'
    allowed_domains = ['bang.dangdang.com']
    base_url = 'http://bang.dangdang.com/books/fivestars/01.00.00.00.00.00-recent30-0-0-1-{offset}'

    def start_requests(self):
        for offset in range(1, 25):
            url = self.base_url.format(offset=offset)
            yield scrapy.Request(url)

    def parse(self, response):
        selectors = response.css('.bang_list li')
        for selector in selectors:
            l = BookLoader(selector=selector)
            l.add_css('image_url', '.pic img::attr(src)')
            l.add_css('title', '.name a::attr(title)')
            l.add_css('link', '.name a ::attr(href)')
            first_pub = l.nested_xpath('.//div[contains(@class,"publisher_info")][1]')
            first_pub.add_css('author', 'a::attr(title)')
            second_pub = l.nested_xpath('.//div[contains(@class,"publisher_info")][2]')
            second_pub.add_css('pub_date', 'span::text')
            second_pub.add_css('publisher', 'a::text')
            l.add_css('price_n', '.price_n::text')
            l.add_css('price_r', '.price_r::text')
            l.add_css('price_s', '.price_s::text')
            yield l.load_item()


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
    process = CrawlerProcess(settings=settings)
    process.crawl(Dangdangtop500Spider)
    process.start()
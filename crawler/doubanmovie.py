# -*- coding: utf-8 -*-
"""
    爬取豆瓣电影 Top 250
    链接: https://movie.douban.com/top250?start=0
    Scrapy API: ItemLoader, DownloaderMiddleware, Feed Export
    需设置 User-Agent
"""
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from scrapy.crawler import CrawlerProcess


class MovieItem(scrapy.Item):
    image_urls = scrapy.Field()
    title = scrapy.Field()
    info = scrapy.Field()
    rating = scrapy.Field()
    quote = scrapy.Field()


class MovieLoader(ItemLoader):
    default_item_class = MovieItem
    default_output_processor = TakeFirst()
    info_in = MapCompose(str.strip)
    info_out = Join()


class DoubanmovieSpider(scrapy.Spider):
    name = 'doubanmovie'
    allowed_domains = ['movie.douban.com']
    base_url = 'https://movie.douban.com/top250?start={offset}'

    def start_requests(self):
        for offset in range(0, 250, 25):
            url = self.base_url.format(offset=offset)
            yield scrapy.Request(url)

    def parse(self, response):
        movies = response.css('.item')
        for movie in movies:
            l = MovieLoader(selector=movie)
            l.add_css('image_urls', '.pic a img::attr(src)')
            l.add_css('title', '.title::text')
            l.add_css('info', '.bd p::text')
            l.add_css('rating', '.rating_num::text')
            l.add_css('quote', '.inq::text')
            item = l.load_item()
            print(item['title'])
            yield item


DOWNLOADER_MIDDLEWARES = {
   'utils.middlewares.UserAgentMiddleware': 543,
}
settings = dict(
    LOG_ENABLED=False,
    FEED_URI = 'top250.json',                           # 导出文件路径
    FEED_FORMAT = 'json',                               # 导出数据格式
    FEED_EXPORT_ENCODING = 'UTF8',                      # 导出文件编码
    DOWNLOADER_MIDDLEWARES=DOWNLOADER_MIDDLEWARES,
)


if __name__ == "__main__":
    process = CrawlerProcess(settings=settings)
    process.crawl(DoubanmovieSpider)
    process.start()
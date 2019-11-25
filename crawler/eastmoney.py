# -*- coding: utf-8 -*-
"""
    爬取东方财富网新闻, 并保存为markdown格式文件
    索引: http://stock.eastmoney.com/news/cmggs.html
    文章: http://stock.eastmoney.com/a/201911101286988247.html
"""
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess


class EastmoneySpider(CrawlSpider):
    name = 'eastmoney'
    start_urls = ['http://stock.eastmoney.com/news/cmggs.html']

    rules = (
        Rule(LinkExtractor(restrict_css='a.page-btn'), follow=True),            # 下一页
        Rule(LinkExtractor(restrict_css='.title a'), callback='parse_item'),    # 文章链接
    )

    def parse_item(self, response):
        item = {}
        item['filename'] = response.css('.newsContent h1::text').get()
        item['html'] = response.css('#ContentBody').get()
        print(item['filename'])
        return item


ITEM_PIPELINES = {
    'utils.pipelines.MarkdownPipeline': 300,
}
settings = dict(
    LOG_ENABLED=False,
    ITEM_PIPELINES=ITEM_PIPELINES,
    MARKDOWNS_STORE='news',
)


if __name__ == "__main__":
    process = CrawlerProcess(settings=settings)
    process.crawl(EastmoneySpider)
    process.start()
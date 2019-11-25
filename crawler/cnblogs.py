# -*- coding: utf-8 -*-
"""
    爬取博客园文章并保存为markdown格式文件, 爬取主页的前5页
    链接: http://cnblogs.com/sitehome/p/1
    Scrapy API: LinkExtractor, pipelines
    html文本转markdown: html2text库
"""
import os

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess


class CnblogsSpider(CrawlSpider):
    name = 'cnblogs'
    allowed_domains = ['cnblogs.com']
    start_urls = ['http://cnblogs.com/']

    rules = (
        Rule(LinkExtractor(allow='/sitehome/p/[1-5]*$'), follow=True),          # 爬取主页前5页博客文章
        Rule(LinkExtractor(restrict_css='.titlelnk'), callback='parse_item'),
    )

    def parse_item(self, response):
        item = {}
        title = response.css('#cb_post_title_url::text').get()
        post = response.css('.post').get()
        print(title)
        item['filename'] = title
        item['html'] = post
        return item


ITEM_PIPELINES = {
    'utils.pipelines.MarkdownPipeline': 300,
}
settings = dict(
    LOG_ENABLED=False,
    ITEM_PIPELINES=ITEM_PIPELINES,
    MARKDOWNS_STORE='posts',            # 文章保存路径
)


if __name__ == "__main__":
    process = CrawlerProcess(settings=settings)
    process.crawl(CnblogsSpider)
    process.start()
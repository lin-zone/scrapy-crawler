# -*- coding: utf-8 -*-
"""
    爬取微信文章
    链接: https://weixin.sogou.com/
    Ajax加载, XHR URL: https://weixin.sogou.com/pcindex/pc/pc_0/1.html
"""
from itertools import count

import scrapy
from scrapy.crawler import CrawlerProcess


class WeixinSpider(scrapy.Spider):
    name = 'weixin'
    allowed_domains = ['weixin.sogou.com', 'mp.weixin.qq.com']
    base_url = 'https://weixin.sogou.com/pcindex/pc/pc_0/{offset}.html'
    offset = count(1)

    def get_request(self):
        url = self.base_url.format(offset=next(self.offset))
        return scrapy.Request(url)

    def start_requests(self):
        yield self.get_request()

    def parse(self, response):
        selectors = response.css('div.txt-box a')
        for selector in selectors:
            yield response.follow(selector, callback=self.parse_item)
        yield self.get_request()
        
    def parse_item(self, response):
        item = {}
        item['filename'] = response.css('#activity-name::text').get().strip('\"').strip()
        item['html'] = response.css('#img-content').get()
        print(item['filename'])
        yield item


ITEM_PIPELINES = {
    'utils.pipelines.MarkdownPipeline': 300,
}
DOWNLOADER_MIDDLEWARES = {
   'utils.middlewares.UserAgentMiddleware': 543,
}
settings = dict(
    # LOG_ENABLED=False,
    ITEM_PIPELINES=ITEM_PIPELINES,
    DOWNLOADER_MIDDLEWARES=DOWNLOADER_MIDDLEWARES,
    MARKDOWNS_STORE='news',                         # 新闻保存路径
)


if __name__ == "__main__":
    process = CrawlerProcess(settings=settings)
    process.crawl(WeixinSpider)
    process.start()
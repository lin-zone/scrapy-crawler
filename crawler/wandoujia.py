# -*- coding: utf-8 -*-
"""
    爬取豌豆荚app信息
    所有应用: https://www.wandoujia.com/category/app
    应用分类: https://www.wandoujia.com/category/5029_716
    使用Chrome的F12调试功能 -> Network -> XHR, 
    点击 查看更多 可以看到加载出XHR文件
    链接示例: https://www.wandoujia.com/wdjweb/api/category/more?catId=5029&subCatId=716&page=2&ctoken=PABRNsZbToZ1HQgJIUYeV34d
    请求XHR文件需设置ctoken参数, 其值与网站设置的cookies值里的ctoken一致
"""
import re
import json

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.crawler import CrawlerProcess


class AppItem(scrapy.Item):
    icon = scrapy.Field()               # 图标链接
    name = scrapy.Field()               # 应用名
    install_count = scrapy.Field()      # 下载次数
    size = scrapy.Field()               # 应用大小, 单位MB
    desc = scrapy.Field()               # 应用简介
    cate = scrapy.Field()               # 分类
    child_cate = scrapy.Field()         # 子分类


class AppLoader(ItemLoader):
    default_item_class = AppItem
    default_output_processor = TakeFirst()


class WandoujiaSpider(scrapy.Spider):
    name = 'wandoujia'
    allowed_domains = ['www.wandoujia.com']
    start_urls = ['https://www.wandoujia.com/category/app']
    more_url = 'https://www.wandoujia.com/wdjweb/api/category/more'
    start_page = 2

    def parse(self, response):
        parent_cates = response.css('.parent-cate')
        for parent_cate in parent_cates:
            parent_cate_title = parent_cate.css('.cate-link').attrib['title']   # 分类
            child_cates = parent_cate.css('.child-cate a')
            for child_cate in child_cates:
                child_cate_title = child_cate.attrib['title']                   # 子分类
                cate_link = child_cate.attrib['href']
                m = re.match('.*/(\d+)_(\d+)', cate_link)
                parent_cate_id, child_cate_id = m.groups()                      # 分类id
                meta = dict(
                    parent_cate_title=parent_cate_title,
                    child_cate_title=child_cate_title,
                    parent_cate_id=parent_cate_id,
                    child_cate_id=child_cate_id,
                )
                yield response.follow(
                    child_cate,
                    callback=self.get_category,
                    meta=meta,
                )

    def get_category(self, response):
        yield from self.parse_category(response, response)      # 应用分类, HTML
        yield from self.get_more_category(response)             # 查看更多, XHR

    def parse_category(self, response, selector):
        apps = selector.css('li.card')
        for app in apps:
            l = AppLoader(selector=app)
            l.add_css('icon', 'img.icon::attr(src)')
            l.add_css('name', 'a.name::text')
            l.add_css('install_count', '.meta span.install-count::text')
            l.add_css('size', '.meta span:last-of-type::text')
            l.add_css('desc', 'div.comment::text')
            l.add_value('cate', response.meta['parent_cate_title'])
            l.add_value('child_cate', response.meta['child_cate_title'])
            item = l.load_item()
            print(item['name'])
            yield item

    def get_more_category(self, response):
        meta = response.meta
        if 'page' in meta:          # 设置page作为偏移量, 从第2页开始, 以后每次加一
            meta['page'] += 1
        else:
            meta['page'] = 2
        formdata = dict(
            catId=meta['parent_cate_id'],
            subCatId=meta['child_cate_id'],
            page=str(meta['page']),
            ctoken=self.cookies['ctoken'],
        )
        yield scrapy.FormRequest(
            self.more_url,
            method='GET',
            callback=self.parse_more_category,
            meta=meta,
            formdata=formdata,
        )

    def parse_more_category(self, response):
        js = json.loads(response.text)
        page = js['data']['currPage']
        if int(page) < 2:
            return
        content = js['data']['content']
        selector = scrapy.Selector(text=content)
        yield from self.parse_category(response, selector)
        yield from self.get_more_category(response)


DOWNLOADER_MIDDLEWARES = {
    'utils.middlewares.UserAgentMiddleware': 543,
    'utils.middlewares.FirefoxSetCookiesMiddleware': 544,
}
settings = dict(
    LOG_ENABLED=False,
    DOWNLOAD_DELAY=0.5,             # 设置延迟, 下载太快会请求失败
    FEED_URI='wandoujia.json',
    FEED_EXPORT_ENCODING='UTF8',
    FEED_FORMAT='json',
    DOWNLOADER_MIDDLEWARES=DOWNLOADER_MIDDLEWARES,
)


if __name__ == "__main__":
    process = CrawlerProcess(settings=settings)
    process.crawl(WandoujiaSpider)
    process.start()
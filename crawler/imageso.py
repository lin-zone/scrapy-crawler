# -*- coding: utf-8 -*-
"""
    输入关键词爬取360图片
    运行: python imageso.py [query] [index]
    链接: https://image.so.com/
    请求示例链接: https://image.so.com/j?q=lol&pn=100&sn=1
    Scrapy API: ImagesPipeline
    下载jpg图片需安装pillow库
"""
import json

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.pipelines.images import ImagesPipeline
from scrapy.crawler import CrawlerProcess


class ImagesoSpider(scrapy.Spider):
    name = 'imageso'
    step = 100
    base_url = 'https://image.so.com/j?q={query}&pn={step}&sn={start}'

    def __init__(self, query, index=1500):
        self.query = query          # 搜索关键词
        self.index = int(index)     # 图片最大索引值

    def start_requests(self):
        for start in range(1, self.index, self.step):
            step = min(self.index - start + 1, self.step)
            url = self.base_url.format(query=self.query, start=start, step=step)
            yield scrapy.Request(url)

    def parse(self, response):
        data = json.loads(response.text)
        if not data.get('total'):           # 如果没有数据关闭爬虫
            raise CloseSpider()
        for item in data['list']:
            yield item


class ImagesoImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        image_url = item['img']
        return scrapy.Request(image_url, meta=dict(index=item['index']))

    def file_path(self, request, response=None, info=None):
        query = info.spider.query
        index = request.meta['index']
        path = f'{query}/{index}.jpg'
        print(path)
        return path


ITEM_PIPELINES = {
    'imageso.ImagesoImagesPipeline': 1,
}
settings = dict(
    LOG_ENABLED=False,
    ITEM_PIPELINES=ITEM_PIPELINES,
    IMAGES_STORE='images',              # 图片保存目录
    DOWNLOAD_TIMEOUT=30,                # 最大超时时间
    RETRY_ENABLED=False,                # 关闭失败重试
    IMAGES_MIN_WIDTH=1280,              # 图片宽度最小像素
    IMAGES_MIN_HEIGHT=720,              # 图片高度最小像素
)


if __name__ == "__main__":
    import sys

    query = sys.argv[1]
    if len(sys.argv) > 2:
        index = sys.argv[2]
    else:
        index = 1500
    process = CrawlerProcess(settings=settings)
    process.crawl(ImagesoSpider, query=query, index=index)
    process.start()
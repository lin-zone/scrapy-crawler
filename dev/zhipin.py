# -*- coding: utf-8 -*-
import scrapy


GUANGZHOU = "c101280100"
PYTHON = "python"
url_fmt = "https://www.zhipin.com/{city}/?query={query}&page={page}&ka=page-{page}"


class ZhipinSpider(scrapy.Spider):
    
    name = 'zhipin'
    allowed_domains = ['www.zhipin.com']

    def start_requests(self, response):
        for page in range(1, self.page):
            url = url_fmt.format(city=GUANGZHOU, query=PYTHON, page=page)
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        response.css(".name")

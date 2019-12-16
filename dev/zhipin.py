# -*- coding: utf-8 -*-
"""
手机端请求:
    1. 使用mitmproxy抓包获取boss直聘的url请求
        https://www.zhipin.com/c101280100-p100109/?ka=position-100109
        https://www.zhipin.com/wapi/zpgeek/mobile/jobs.json?page=3&city=101280100&query=Python
    2. 需要设置cookies, 否则会返回错误信息 {"code":37,"message":"您的访问行为异常"}

PC端请求
    https://www.zhipin.com/c101280100/?query=python&page=3&ka=page-3
"""
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

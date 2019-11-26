from urllib.parse import urlparse

from selenium import webdriver
from fake_useragent import UserAgent


class UserAgentMiddleware(object):
    """设置随机的User-Agent"""
    ua = UserAgent()

    def process_request(self, request, spider):
        request.headers['User-Agent'] = self.ua.random


class FirefoxSetCookiesMiddleware(object):
    """使用Selenium驱动打开Firefox浏览器获取网页Cookies
    Firefox浏览器版本 69.0.1, geckodriver版本要和浏览器版本对应
    geckodriver下载: https://github.com/mozilla/geckodriver/releases
    Chrome浏览器的headless模式好像出了点问题, 就用Firefox浏览器好了
    """

    def process_request(self, request, spider):
        if not hasattr(spider, 'cookies'):
            options = webdriver.FirefoxOptions()
            options.add_argument('--headless')              # 启动无头模式
            browser = webdriver.Firefox(options=options)
            # 通过主页的url获取cookies, 其他链接可能无法正确获取cookies
            result = urlparse(request.url)
            base_url = '{}://{}'.format(result.scheme, result.netloc)
            browser.get(base_url)
            raw_cookies = browser.get_cookies()
            # 将selenium获得的cookies格式转换为scrapy需要的cookies格式
            spider.cookies = {c['name']: c['value'] for c in raw_cookies}
            browser.quit()                                  # 关闭浏览器
        request.cookies = spider.cookies
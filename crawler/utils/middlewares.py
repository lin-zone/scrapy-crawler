from fake_useragent import UserAgent


class UserAgentDownloadMiddleware(object):
    ua = UserAgent()

    def process_request(self, request, spider):
        request.headers['User-Agent'] = self.ua.random
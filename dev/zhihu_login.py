import time
from http import cookiejar
from urllib.parse import quote

import requests


headers = {
    "Host": "www.zhihu.com",
    "Referer": "https://www.zhihu.com/",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36"
}
# 使用登录cookie信息
session = requests.session()
session.cookies = cookiejar.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print("Cookie 未能加载")


def get_xsrf():
    '''_xsrf 是一个动态变化的参数'''
    index_url = 'https://www.zhihu.com/signin?next=%2F'
    # 获取登录时需要用到的_xsrf
    r = session.get(index_url, headers=headers)
    xsrf = r.cookies['_xsrf']
    return xsrf


# xsrf = get_xsrf()
# print(xsrf)

# def login():
#     url="https://www.zhihu.com/signup?next=%2F"
#     data = dict(
#         email='1264260543@qq.com',
#         password='1234qwer!@#$',
#     )
#     r = requests.post(url, data=data)
#     print(r.status_code)
#     html = r.text
#     with open('index.html', 'w', encoding='UTF8') as f:
#         f.write(html)


def login(account, password):
    xsrf = get_xsrf()
    headers["X-Xsrftoken"] = xsrf
    headers["X-REquested-With"] = "XMLHttpRequest"
    url="https://www.zhihu.com/signup?next=%2F"
    time_stamp = str(int((time.time() * 1000)))
    data = {
        "client_id": "c3cef7c66a1843f8b3a9e6a1e3160e20",
        "grant_type": "password",
        "timestamp": time_stamp,
        "source": "com.zhihu.web",
        "password": password,
        "username": quote(account),
        # "captcha": "",
        "lang": "en",
        # "lang": "cn",
        "ref_source": "homepage",
        "utm_source": "",
        # "signature": self._get_signature(time_stamp),
        # 'captcha': captcha
    }
    r = session.post(url, data=data, headers=headers)
    print(r.status_code)
    # print(r.json())
    session.cookies.save()
    # with open('index.html', 'w', encoding='UTF8') as f:
    #     f.write(r.text)

password = input('password:')
login('1264260543@qq.com', password)
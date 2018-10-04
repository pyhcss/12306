# coding=utf-8

'''
*-*----------------------------免责声明-------------------------------*-*
*-*以下代码仅用于本人测试留档使用 任何单位及个人使用本段代码产生的一切后果自行负责*-*
*-*经分析 12306验证码读取 校验与账户密码校验是分离的 于是想到 借用12306验证码　*-*
*-*----------------------------开始实现-------------------------------*-*
'''

import re
import json
import random
import urllib
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.httpclient


class IndexHandler(tornado.web.RequestHandler):
    """返回html代码"""
    def get(self):
        text = "<form method='POST' action='/image'> \
                <img src='/image' alt='验证码'><br><br> \
                <input type='hidden' name='captcha_id' value=''> \
                <input type='text' name='captcha_text'></input> \
                <input type='submit'></input> \
                </form>"
        text2 = "<script></script>"                 # 在提交之前jquery动态改变验证码id的值
                                                    # 太麻烦不写了 测试直接从cookie取数据
                                                    # 用户点击 生成值的前端逻辑也忽略
        self.write(text)                            # 值存在cookie中passport中


class ImageHandler(tornado.web.RequestHandler):
    """测试类,获取验证码"""
    def get(self):
        """获取验证码"""
        captchahandler = CaptchaHandler()           # 创建生成验证码对象
        dict_data = captchahandler.get_captcha()    # 获取验证码返回值
        self.set_cookie("passport",dict_data["passport"])# 设置cookie
        self.write(dict_data["image"])              # 返回图片数据

    def post(self):
        """校验验证码"""
        passport_id = self.get_cookie("passport","")# 获取cookie中passport值
        passport_value = self.get_argument("captcha_text","")# 获取用户点击文本值
        if not passport_id or not passport_value:   # 获取不到返回错误信息
            return self.write({"errcode":"404","errmsg":"cookie error"})
        captchahandler = CaptchaHandler()           # 创建请求对象
        resp = captchahandler.captcha(passport_id,passport_value)# 拿到返回值
                                                    # 写入返回值 可根据需要判断调整
        self.write({"errcode":resp["result_code"],"errmsg":resp["result_message"]})


class CaptchaHandler(object):
    """获取及校验12306验证码 鉴于测试全部简写 异步单例等均不实现"""

    def __init__(self):
        self.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60"}

    def get_captcha(self):
        """获取验证码"""
        url = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&"
        url += str(random.random())                 # 添加自定义随机数
        request = tornado.httpclient.HTTPRequest(url,headers=self.headers)# 构建请求对象
        http_client = tornado.httpclient.HTTPClient()# 创建客户端对象
        resp = http_client.fetch(request)           # 发送请求拿到响应
                                                    # 拿到set-Cookie中的_passport_ct字段值
        passport =  re.search(r"_passport_ct=(\w+);",resp.headers["Set-Cookie"]).group(1)
        image_data = resp.body                      # 拿到图片数据
        return {"passport":passport,"image":image_data}# 返回结果

    def captcha(self,id,value):
        """校验验证码"""
        url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
        data = {                                    # 创建数据内容
            "answer":value,                         # 验证码值
            "login_site":"E",                       # 固定值
            "rand":"sjrand"                         # 固定值
        }
        headers = self.headers
        headers["Cookie"] = "_passport_ct="+id      # 构建请求对象
        request = tornado.httpclient.HTTPRequest(url,method="POST",headers=headers,body=urllib.urlencode(data))
        http_client = tornado.httpclient.HTTPClient()# 创建客户端对象
        resp = http_client.fetch(request).body      # 发送请求拿到响应
        return json.loads(resp)                     # 返回数据


if __name__ == "__main__":
    app = tornado.web.Application(
        [
            (r"^/",IndexHandler),
            (r"^/image",ImageHandler),
        ],
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.current().start()

# *-*----------------------------测试成功-------------------------------*-*
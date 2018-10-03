# coding=utf-8

import json
import urllib
import urllib2
import random
import cookielib

USERNAME = ""                                               # 账号
PASSWORD = ""                                               # 密码

class AutoLogin(object):
    """12306自动登录模块"""

    def __init__(self):
        """初始化方法"""
        cookie = cookielib.CookieJar()                      # 构建cookiejar对象 用来保存cookie对象
        cookie_handler = urllib2.HTTPCookieProcessor(cookie)# 构建自定义cookie处理器对象 用来处理cookie
        self.opener = urllib2.build_opener(cookie_handler)  # 构建opener对象 用来发送请求
        self.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60"}
        # urllib2.install_opener(opener)                      # 设置自定义opener为全局 之后可直接使用urllib2.urlopen
        self.newapptk = None

    def get_captcha(self):
        """获取验证码图片保存到本地"""
        url = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&"
        url += str(random.random())                         # 添加自定义随机数
        request = urllib2.Request(url,headers=self.headers) # 创建自定义报头信息
        image_data = self.opener.open(request).read()       # 发送请求获取内容
        with open("./12306.jpg","w") as f:                  # 写入到本地文件
            f.write(image_data)

    def get_captcha_text(self):
        """人工输入验证码"""
        print "-----------图片编号-----------"
        print "-----1-----3-----5-----7-----"
        print "-----2-----4-----6-----8-----"
        print "-----------图片编号-----------"
        data = raw_input("请输入图片编号,例如(138):")         # 输入图片编号
        text_list = []                                      # 建立文本列表
        if "1" in data:                                     # 判断输入内容把值加入列表
            text_list.append(str(random.randint(30,40)))
            text_list.append(str(random.randint(40,50)))
        if "2" in data:
            text_list.append(str(random.randint(30,40)))
            text_list.append(str(random.randint(110,120)))
        if "3" in data:
            text_list.append(str(random.randint(107,115)))
            text_list.append(str(random.randint(40,50)))
        if "4" in data:
            text_list.append(str(random.randint(107, 115)))
            text_list.append(str(random.randint(110, 120)))
        if "5" in data:
            text_list.append(str(random.randint(180,185)))
            text_list.append(str(random.randint(40, 50)))
        if "6" in data:
            text_list.append(str(random.randint(180,185)))
            text_list.append(str(random.randint(110,120)))
        if "7" in data:
            text_list.append(str(random.randint(248,260)))
            text_list.append(str(random.randint(40, 50)))
        if "8" in data:
            text_list.append(str(random.randint(248,260)))
            text_list.append(str(random.randint(110,120)))
        return ",".join(text_list)                          # 拼接列表组成验证码文本

    def login_captcha(self,text):
        """校验验证码"""
        url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
        data = {                                            # 创建数据内容
            "answer":text,                                  # 验证码值
            "login_site":"E",                               # 固定值
            "rand":"sjrand"                                 # 固定值
        }                                                   # 创建自定义请求对象
        request = urllib2.Request(url,data=urllib.urlencode(data),headers=self.headers)
        data_json = self.opener.open(request).read()        # 发送请求 获取json数据
        data = json.loads(data_json)                        # 解析json数据
        if data["result_code"] == "4":                      # 如果返回值为4
            print "验证码校验成功"                            # 校验成功
            return "0"
        else:                                               # 否则校验失败
            print "验证码校验失败"
            return "captcha error"

    def get_uamtk(self):
        """发送账号密码请求"""
        url = "https://kyfw.12306.cn/passport/web/login"
        data = {                                            # 创建数据内容
            "username":USERNAME,                            # 账户名
            "password":PASSWORD,                            # 密码
            "appid": "otn"                                  # 固定值
        }                                                   # 创建自定义请求对象
        request = urllib2.Request(url,data=urllib.urlencode(data),headers=self.headers)
        data_json = self.opener.open(request).read()        # 发送请求 获取json数据
        data = json.loads(data_json)                        # 解析json数据
        if data["result_code"] == 0:                        # 如果返回值为0
            print "账号密码校验成功"                          # 校验成功
            return "0"
        else:                                               # 否则校验失败
            print "账号密码校验失败"
            return "user pwd error"

    def get_newapptk(self):
        """获取newapptk"""
        url = "https://kyfw.12306.cn/passport/web/auth/uamtk"
        data = {"appid":"otn"}                              # 固定参数
        request = urllib2.Request(url,data=urllib.urlencode(data),headers=self.headers)
        data_json = self.opener.open(request).read()        # 发送请求 获取json数据
        data = json.loads(data_json)                        # 解析json数据
        if data["result_code"] == 0:                        # 如果返回值为0
            self.newapptk = data["newapptk"]
            print "newapptk获取成功"                         # 校验成功
            return "0"
        else:                                               # 否则校验失败
            print "newapptk获取失败"
            return "user pwd error"

    def get_username(self):
        """获取用户名 最后一步验证"""
        url = "https://kyfw.12306.cn/otn/uamauthclient"
        data = {"tk":self.newapptk}                         # 上一步获取到的值
        request = urllib2.Request(url,data=urllib.urlencode(data),headers=self.headers)
        data_json = self.opener.open(request).read()        # 发送请求 获取json数据
        data = json.loads(data_json)                        # 解析json数据
        if data["result_code"] == 0:                        # 如果返回值为0
            print "用户名获取成功"                            # 校验成功
            print data["username"] + u" 你好"
            return "0"
        else:                                               # 否则校验失败
            print "用户名获取失败"
            return "user pwd error"

    def get_html(self):
        url = "https://kyfw.12306.cn/otn/index/initMy12306"
        request = urllib2.Request(url,headers=self.headers) # 构建自定义请求对象
        response = self.opener.open(request).read()         # 获取html文本
        print response                                      # 打印html

    def main(self):
        """调度方法"""
        self.get_captcha()                                  # 获取验证码图片
        text = self.get_captcha_text()                      # 获取验证码文本
        rest = self.login_captcha(text)                     # 发送请求校验验证码
        if rest != "0":                                     # 如果返回值不是0
            return "验证码模块失败"                           # 结束函数
        rest = self.get_uamtk()                             # 发送账号密码请求
        if rest != "0":                                     # 如果返回值不是0
            return "账号密码模块失败"                         # 结束函数
        rest = self.get_newapptk()                          # 获取newapptk
        if rest != "0":                                     # 如果返回值不是0
            return "获取newapptk模块失败"                     # 结束函数
        rest = self.get_username()                          # 获取用户名
        if rest != "0":                                     # 如果返回值不是0
            return "获取用户名模块失败"                       # 结束函数
        self.get_html()
        return "0"


if __name__ == "__main__":
    autologin = AutoLogin()
    rest = autologin.main()
    if rest != "0":
        print rest
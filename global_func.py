# coding=utf-8

import smtplib
import pymysql
import urllib2
import cookielib
from global_data import GLOBAL_DB
from global_data import GLOBAL_163
from email.mime.text import MIMEText


class Global_Opener(object):
    """全局opener对象 单例模式"""
    _instance = None                                            # 判断是否生成过对象
    _first_init = True                                          # 是否首次初始化

    def __new__(cls):
        """创建单例模式"""
        if cls._instance == None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化"""
        if self._first_init:
            _cookie = cookielib.CookieJar()                       # 构建cookiejar对象 用来保存cookie对象
            _cookie_handler = urllib2.HTTPCookieProcessor(_cookie)# 构建自定义cookie处理器对象 用来处理cookie
            self._opener = urllib2.build_opener(_cookie_handler)  # 构建opener对象 用来发送请求
            self._first_init = False

    def open(self,url,data=None,headers={}):
        """
        自定义UA 创建request对象发送请求拿到结果
        data:       urlencode类型      post请求数据 不传递则默认get请求
        headers:    {}                需要自定义的请求报头信息
        return:     response对象       服务器响应数据
        """
        headers["User-Agent"] = 'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
        request = urllib2.Request(url,headers=headers,data=data)
        return self._opener.open(request,timeout=20)


class MySqldb(object):
    """全局mysql对象 单例模式"""
    _instance = None                                            # 判断是否生成过对象
    _first_init = True                                          # 是否首次初始化

    def __new__(cls):
        """创建单例模式"""
        if cls._instance == None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化数据库链接"""
        if self._first_init:
            self._db_client = pymysql.Connection(**GLOBAL_DB)
            self._cursor = self._db_client.cursor()
            self._first_init = False

    def query(self,*args,**kwargs):
        """
        查询单条数据 返回查询结果
        *args:           按照mysql中execute参数传递
        return:          查询结果元组
        """
        self._cursor.execute(*args,**kwargs)
        return self._cursor.fetchone()

    def close(self):
        """关闭客户端链接 所有程序最后调用"""
        self._db_client.close()
        self._cursor.close()


def sendemail(com):
    """
    smtp服务发送邮件
    com: "" 主题
    return: "发送成功" or "发送失败"
    """
    smtp_address = "smtp.163.com"                               # 163smtp地址
    from_mail = GLOBAL_163["from_mail"]                         # 发件方账号
    from_pwd = GLOBAL_163["from_pwd"]                           # 发件方密码
    to_mail = GLOBAL_163["to_mail"]                             # 收件方账号
                                                                # 邮件内容
    if com == "火车票预定情况":
        message = MIMEText("12306预定成功,请及时登录12306查看订单及支付订单", "plain", "utf-8")
    else:
        message = MIMEText("12306预定出现异常,请及时排查", "plain", "utf-8")
    message["From"] = from_mail
    message["To"] = to_mail
    message["Subject"] = com
    try:
        smtp_server = smtplib.SMTP(smtp_address, port=25)       # 链接163smtp服务
        smtp_server.login(from_mail, from_pwd)                  # 登录账号密码
        smtp_server.sendmail(from_mail, to_mail, message.as_string())# 发送邮件
        smtp_server.close()                                     # 关闭服务
        return "邮件发送成功"
    except Exception as e:
        print e
        return "邮件发送失败"


global_opener = Global_Opener()                                # 创建全局opener实例
global_db = MySqldb()                                          # 创建全局mysql实例


if __name__ == "__main__":
    response = global_opener.open("http://ihome.newzn.cn/login.html").read()
    print response

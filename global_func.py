# coding=utf-8

import pymysql
import urllib2
import cookielib

from global_data import GLOBAL_DB


class Global_Opener(object):
    """全局opener对象"""
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
        """自定义UA 发送请求拿到结果"""
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60"
        request = urllib2.Request(url,headers=headers,data=data)
        return self._opener.open(request)


class MySqldb(object):
    """全局mysql对象"""
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
        """查询单条数据 返回查询结果 返回元组"""
        self._cursor.execute(*args,**kwargs)
        return self._cursor.fetchone()

    def close(self):
        """关闭客户端链接 所有程序最后调用"""
        self._db_client.close()
        self._cursor.close()


def _query_code(date,from_station,to_station):
    """查询起始站和目的站代号 返回查询结果集"""
    start = global_db.query("select name_code from station where name=%s", (from_station))
    end = global_db.query("select name_code from station where name=%s", (to_station))
    data = [                                                   # 格式化查询信息
        {"leftTicketDTO.train_date": date},                    # 出发日期
        {"leftTicketDTO.from_station": start[0]},              # 出发站代号
        {"leftTicketDTO.to_station": end[0]},                  # 到达站代号
        {"purpose_codes": "ADULT"}                             # 固定值
    ]
    global_db.close()
    return data


global_opener = Global_Opener()                                # 创建全局opener实例
global_db = MySqldb()                                          # 创建全局mysql实例
global_query_code = _query_code                                # 全局查询火车站代号


if __name__ == "__main__":
    response = global_opener.open("http://ihome.newzn.cn/login.html").read()
    print response

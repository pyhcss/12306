# coding=utf-8

import pymysql
from global_data import GLOBAL_DB


class NameToMysql(object):
    """存储所有车站名称到mysql"""

    def __init__(self):
        """初始化方法"""
        self.db_client = pymysql.Connection(**GLOBAL_DB)
        self.cursor = self.db_client.cursor()

    def name_mysql(self):
        """储存车站名到数据库"""
        with open("station.txt","r") as f:
            text = f.read()
        name_list = text.split("@")
        for i in name_list:
            data = i.split("|")
            self.cursor.execute("insert into station (start_code,name,name_code,pinyin,start,card_id) values(%s,%s,%s,%s,%s,%s)",(data[0],data[1],data[2],data[3],data[4],data[5]))
            self.db_client.commit()

    def close(self):
        """关闭数据库链接"""
        self.cursor.close()
        self.db_client.close()


if __name__ == "__main__":
    name_to_mysql = NameToMysql()
    name_to_mysql.name_mysql()
    name_to_mysql.close()
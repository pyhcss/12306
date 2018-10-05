# coding=utf-8

import json
import time
import urllib
import datetime
from global_func import global_opener,global_db

import sys                                                  # 解决ascii问题
reload(sys)
sys.setdefaultencoding("utf-8")


class AutoQuery(object):
    """自动查询车票情况"""

    def __init__(self):
        """初始化方法"""
        self.data = None                                    # 初始化查询数据

    def input_text(self):
        """获取出发信息"""
        date = raw_input("请输入出发日期(例20181001):").replace(" ", "")
                                                            # 格式化出发日期
        date = time.strftime("%Y-%m-%d",time.strptime(date,"%Y%m%d"))
        date2 = datetime.datetime.now().strftime("%Y-%m-%d")# 生成当前日期
        if date < date2:                                    # 出发日期小于当前日期
            print "出发时间不能晚于当前时间 请重新输入"         # 重新启动函数
            self.input_text()
        else:                                               # 提示输入出发站目的站
            start = raw_input("请输入出发站(例北京):").replace(" ", "").replace("站", "")
            end = raw_input("请输入目的站(例天津):").replace(" ", "").replace("站", "")
            try:                                            # 从数据库获取标准码
                start = global_db.query("select name_code from station where name=%s",(start))
                end = global_db.query("select name_code from station where name=%s",(end))
                self.data = [                               # 格式化查询信息
                    {"leftTicketDTO.train_date":date},      # 出发日期
                    {"leftTicketDTO.from_station":start[0]},# 出发站代号
                    {"leftTicketDTO.to_station":end[0]},    # 到达站代号
                    {"purpose_codes": "ADULT"}              # 固定值
                ]
            except Exception as e:                          # 数据库查询错误重新执行函数
                print "站点输入有误 请重新输入"
                self.input_text()

    def get_info(self):
        """发送请求获取余票信息"""
        url = "https://kyfw.12306.cn/otn/leftTicket/queryA?"# 构造url
        data_list = [urllib.urlencode(i) for i in self.data]
        url += "&".join(data_list)                          # 拼接url
        response = global_opener.open(url).read()           # 发送请求 获取返回值
        try:
            data = json.loads(response)                     # 解析json对象
        except Exception as e:
            print e                                         # 出错后返回的不是json对象
            print "服务器响应出错 请稍后..."
            time.sleep(10)                                  # 挂起10秒 重新执行
            self.get_info()
        else:                                               # 正常状态返回码
            if data["httpstatus"] == 200 and data["status"] == True:
                data = data["data"]                         # 解析数据 格式化输出
                print "-----------------------------------------------------" \
                      "-----------------------------------------------------" \
                      "----------------------------------"
                print "车次---出发站---到达站---出发时间---到达时间---历时分钟---" \
                      "当日到达---高级软卧---软卧---特等座---一等座---二等座---" \
                      "硬卧---硬座---无座---编号"
                a = 1
                for i in data["result"]:
                    i = i.split("|")
                    print "-----------------------------------------------" \
                          "-----------------------------------------------" \
                          "----------------------------------------------"
                    print "{1:<5}  {2:{0}<4} {3:{0}<4}  {4:<5}      {5:<5}\t" \
                          "{6:<5}\t    {7:<1}\t\t{8:<2}\t {9:<2}\t {10:<2}\t  " \
                          "{11:<2}\t   {12:<2}\t   {13:<2}\t  {14:<2}\t " \
                          "{15:<2}\t{16:<2}".format(unichr(12288),i[3],data["map"][i[6]],
                          data["map"][i[7]],i[8],i[9],i[10],u"是" if i[18] =="1" else u"否",
                          i[21],i[23],i[32],i[31],i[30],i[28],i[29],i[26],int(a))
                    a += 1
            else:                                           # 出错后挂起10秒 重新执行
                print "json解析出错 请稍后..."
                time.sleep(10)
                self.get_info()

    def main(self):
        """调度函数"""
        self.input_text()
        global_db.close()
        self.get_info()


if __name__ == "__main__":
    auto_query = AutoQuery()
    auto_query.main()
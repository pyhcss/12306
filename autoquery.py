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

    def input_text(self):
        """
        从命令行获取出发信息
        return {"date":"2018-10-10","start":"北京","end":"天津"}
        """
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
            try:
                data = {
                    "date":date,                            # 出发时间字符串"2018-10-10"
                    "start":start,                          # 出发站字符串"北京"
                    "end":end,                              # 目的站字符串"天津"
                }
                return data                                 # 从数据库获取车站标准码
            except Exception as e:
                print "站点输入有误 请重新输入"
                self.input_text()                           # 数据库查询错误重新执行函数

    def query_code(self,date,from_station,to_station):
        """
        从数据库查询起始站和目的站代号 格式化查询结果集
        date:"2018-10-10"               出发时间 格式化数据
        from_station:"北京"              出发站  进行sql查询并格式化数据
        to_station:"天津"                目的站  进行sql查询并格式化发送数据
        return:[{"leftTicketDTO.train_date":"2018-10-10"},
                {"leftTicketDTO.from_station":"VPN"},
                {"leftTicketDTO.to_station":"NPV"},
                {"purpose_codes": "ADULT"}
               ]
        """
        start = global_db.query("select name_code from station where name=%s", (from_station))
        end = global_db.query("select name_code from station where name=%s", (to_station))
        data = [                                            # 格式化查询信息
            {"leftTicketDTO.train_date": date},             # 出发日期
            {"leftTicketDTO.from_station": start[0]},       # 出发站代号
            {"leftTicketDTO.to_station": end[0]},           # 到达站代号
            {"purpose_codes": "ADULT"}                      # 固定值
        ]
        global_db.close()                                   # 关闭数据库链接
        print "格式化数据完成"
        return data

    def get_info(self,data):
        """
        发送请求获取所有余票信息
        data: [ {"leftTicketDTO.train_date":"2018-10-10"},
                {"leftTicketDTO.from_station":"VPN"},
                {"leftTicketDTO.to_station":"NPV"},
                {"purpose_codes": "ADULT"}
              ]
        return: {"result":["列车详情1","列车详情2"]}
        """
        while True:
            url = "https://kyfw.12306.cn/otn/leftTicket/queryA?"# 构造url
            data_list = [urllib.urlencode(i) for i in data]     # 遍历数据组成参数列表
            url += "&".join(data_list)                          # 拼接url
            try:
                response = global_opener.open(url).read()       # 发送请求 获取返回值
                data_dict = json.loads(response)                # 解析json对象
            except Exception as e:
                print e                                         # 出错后返回的不是json对象
                print "服务器响应出错 请稍后..."
                time.sleep(5)                                  # 挂起10秒 重新执行
                continue
            else:                                               # 正常状态返回码
                if data_dict["httpstatus"] == 200 and data_dict["status"] == True:
                    print "查询数据完成"
                    return data_dict["data"]                    # 返回数据
                else:                                           # 出错后挂起10秒 重新执行
                    print "json解析出错 请稍后..."
                    time.sleep(10)
                    continue

    def query_train(self,train_code,person,seattype,data):
        """
        查询某趟列车的所有信息
        train_code:["k138",]:   列车简称不区分大小写
        seattype:  "硬座"        坐席类型
        data:    {"result":["列车详情1","列车详情2"]}
        return:  ["列车参数1","列车参数2","列车参数3"...] 详情在 接口分析.txt
        """
        if seattype == "特等座":                             # 判断选择的坐席
            seat = -5
        elif seattype == "一等座":
            seat = -6
        elif seattype == "二等座":
            seat = -7
        elif seattype == "硬卧":
            seat = -9
        elif seattype == "硬座":
            seat = -8
        elif seattype == "无座":
            seat = -11
        for i in train_code:                                # 遍历需要预定的列车
            for x in data["result"]:                        # 遍历所有列车信息
                data_list = x.split("|")                    # 每趟列车格式化成列表
                                                            # 查询符合条件的列车列表
                if i.upper() == data_list[3] and data_list[seat] != "无" and data_list[seat] != "0" and data_list[seat] != "":
                    if data_list[seat] == "有":             # 判断余票多的情况
                        print "列车查询完成"
                        return data_list                    # 返回数据
                    try:
                        if len(person) <= int(data_list[seat]):# 判断余票大于人数的情况
                            print "列车查询完成"
                            return data_list                # 返回数据
                    except Exception as e:
                        pass
        return []

    def format_out(self,data):
        """
        格式化输出所有列车详细信息
        data:   {"result":["列车详情1","列车详情2"]}
        """
        print "-----------------------------------------------------" \
              "-----------------------------------------------------" \
              "----------------------------------"
        print "车次---出发站---到达站---出发时间---到达时间---历时分钟---" \
              "当日到达---高级软卧---软卧---特等座---一等座---二等座---" \
              "硬卧---硬座---无座---编号"
        a = 1
        for i in data["result"]:                            # 遍历所有列车列表数据
            i = i.split("|")                                # 拆分每趟列车的字符串
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

    def main(self):
        """调度函数"""
        data = self.input_text()                            # 从命令行获取出发信息
        data = self.query_code(data["date"],data["start"],data["end"])# 从数据库查询并格式化查询参数
        data = self.get_info(data)                          # 获取所有列车的信息
        self.format_out(data)                               # 格式化输出所有列车信息
        print self.query_train("c2017","二等座",data)        # 从所有列车信息查询某趟列车


if __name__ == "__main__":
    auto_query = AutoQuery()
    auto_query.main()
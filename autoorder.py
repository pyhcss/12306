# coding=utf-8

import re
import time
import json
import urllib
import datetime
from global_func import global_opener
from global_data import GLOBAL_QUERY_DATA as GQD


class AutoOrder(object):
    """自动化下单模块"""

    def checklogin(self):
        """检查是否登录"""
        url = "https://kyfw.12306.cn/otn/login/checkUser"
        data = "_json_att="
        resp = global_opener.open(url,data).read()          # 发送请求 获取返回值
        data = json.loads(resp)                             # 解析数据
        if not data["data"]["flag"]:                        # 判断是否登陆成功
            print "预定验证登录失败"
        else:
            print "预定验证登录成功"

    def destine(self,sercret,date,from_name,to_name):
        """跳转到预定页面"""
        url = "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"
        data = {
            "secretStr":sercret,                            # 车票查询结果中第一个超长字符串
            "train_date":date,                              # 预定时间
                                                            # 当前日期
            "back_train_date":datetime.datetime.now().strftime("%Y-%m-%d"),
            "tour_flag":"dc",                               # 固定值
            "purpose_codes":"ADULT",                        # 固定值
            "query_from_station_name":from_name,            # 搜索时出发站
            "query_to_station_name":to_name,                # 搜索时到达站
            "undefined":""                                  # 默认
        }                                                   # 发送请求 获取数据
        resp = global_opener.open(url,data=urllib.urlencode(data)).read()
        print resp                                          # 返回值为json时正确

    def get_token(self):
        """获取全局token以及校验码"""
        url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        data = "_json_att="
        resp = global_opener.open(url,data=data).read()     # 发送请求 获取响应
        data = {}                                           # 获取token及key
        data["token"] = re.search(r"var globalRepeatSubmitToken = (\w+);",resp).group(1)
        print data["token"]
        data["key"] = re.search(r"'key_check_isChange': '(\w+)'",resp).group(1)
        print data["key"]
        return data

    def get_person(self):
        """获取常用联系人"""
        url = "https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs"
        data = "_json_att="
        resp = global_opener.open(url,data=data).read()     # 发送请求 获取响应
        resp = json.loads(resp)                             # 解析json数据
        data = resp["data"]["normal_passengers"]            # 拿到常用联系人列表
        person_list = []
        for x in GQD["person"]:                             # 查找乘车人信息
            for i in data:                                  # 返回乘车人数据
                if i["passenger_name"] == x:
                    person_list.append(i)
        return person_list                                  # 返回值[{},]

    def order_person_submit(self,person_list,token_key):
        """订票信息预提交"""
        url = "https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo"
        if GQD["seattype"] == "特等座":                      # 判断选择的坐席
            seat = "9"
        elif GQD["seattype"] == "一等座":
            seat = "M"
        elif GQD["seattype"] == "二等座":
            seat = "O"
        elif GQD["seattype"] == "动卧":
            seat = "F"
        elif GQD["seattype"] == "软卧":
            seat = "4"
        elif GQD["seattype"] == "硬卧":
            seat = "3"
        elif GQD["seattype"] == "硬座" or GQD["seattype"] == "无座":
            seat = "1"
        else:
            seat = "O"
        person_info = {                                     # 按要求格式化字符串
            "new":"_".join([",".join([seat,"0",i["passenger_type"],i["passenger_name"],"1",i["passenger_id_no"],i["mobile_no"],"N"]) for i in person_list]),
            "old":"_".join([",".join([i["passenger_name"],"1",i["passenger_id_no"],i["passenger_type"]]) for i in person_list])
        }
        data = {
            "cancel_flag":2,                                # 固定值
            "bed_level_order_num":"000000000000000000000000000000",# 固定值
            "passengerTicketStr":person_info["new"],        # 乘车人信息
            "oldPassengerStr":person_info["old"],           # 多个之间用下划线隔开
            "tour_flag":"dc",                               # 旅客标示 固定值
            "randCode":"",                                  # 默认
            "whatsSelect":1,                                # 默认
            "_json_att":"",                                 # 默认
            "REPEAT_SUBMIT_TOKEN":token_key["token"],       # 全局token
        }                                                   # 发送请求获取返回值
        resp = global_opener.open(url,data=urllib.urlencode(data)).read()
        print resp
        return person_info                                  # 返回组织好的乘车人信息

    def order_train_submit(self,train,person,token_key):
        """订票车次预提交"""
        url = "https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount"
        data = {                                            # 车票日期
            "train_date":time.strftime("%a %b %d %Y %H:%M:%S GMT+0800 (中国标准时间)",time.strptime(GQD["date"],"%Y-%m-%d")),
            "train_no":train[2],                            # 列车代号
            "stationTrainCode":train[3],                    # 简称代号
            "seatType":person["new"][:1],                   # 选择的座位类型
            "fromStationTelecode":train[6],                 # 出发站代号
            "toStationTelecode":train[7],                   # 目的站代号
            "leftTicket":train[12],                         # 查询结果中第二个长代码 第13个值
            "purpose_codes":"00",                           # 目的编号
            "train_location":train[15],                     # 查询结果的第16个值
            "_json_att":"",                                 # 默认
            "REPEAT_SUBMIT_TOKEN":token_key["token"]        # 全局token
        }                                                   # 发送请求拿到响应
        resp = global_opener.open(url,data=urllib.urlencode(data)).read()
        print resp

    def order_submit(self,person,token_key,train):
        """最终提交预定信息"""
        url = "https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue"
        num = len(GQD["person"])
        if num == 1:                                        # 根据人数设置座位类型
            seats = "1A"
        elif num == 2:
            seats = "1D1F"
        elif num == 3:
            seats = "1A1B1C"
        elif num == 4:
            seats = "1D1F2D2F"
        elif num == 5:
            seats = "1A1B1C2A2B"
        else:
            seats = ""
        data = {
            "passengerTicketStr":person["new"],             # 购票信息
            "oldPassengerStr":person["old"],                # 购票信息
            "randCode":"",                                  # 默认
            "purpose_codes":"00",                           # 同上默认
            "key_check_isChange":token_key["key"],          # 检查钥匙是否改变
            "leftTicketStr":train[12],                      # 查询结果中第二个长代码 第13个值
            "train_location":train[15],                     # 查询结果中第16个值
            "choose_seats":seats,                           # 选择座位1A2B1C 只有两排
            "seatDetailType":"000",                         # 座位描述类型
            "whatsSelect":"1",                              # 默认
            "roomType":"00",                                # 不清楚
            "dwAll":"N",                                    # 默认 不清楚
            "_json_att":"",                                 # 默认
            "REPEAT_SUBMIT_TOKEN":token_key["token"]        # 全局token
        }
        resp = global_opener.open(url,data=urllib.urlencode(data)).read()
        print resp


if __name__ == "__main__":
    autoorder = AutoOrder()
    autoorder.checklogin()
    string = "76zFocjSMDxZC7Tmtk38N56fNXsR7yjukuD%2FKev25liHGlAc6ayYVoEDW452gct5ok4CnJiouvIx%0A3eE9x9Dtl62W22C2QWZSKOxPpPDUjkchWCkO2TfnIHC9zkID2jlcDC9IpLkme33AR46nHWElWsWQ%0Ahuwlqg8EXYtYu1%2FpUoX1LZlt38jrW7T2dLIJ2udKE%2FVb6N6rjsagLT7Fwjkf7IqBgXG7ZG5MFwBk%0AZgjGbW4dQOMgHBrRrQsmPZFEJN%2FP"
    autoorder.destine(string,"2018-10-15","北京","天津")
    autoorder.get_token()
    list = [{"passenger_type":"1","passenger_name":"","passenger_id_no":"","mobile_no":""},{"passenger_type":"1","passenger_name":"","passenger_id_no":"","mobile_no":""}]
    token_key = {"token":"OKDJSFUIFNEIDFOIAWMDWAD"}
    autoorder.order_person_submit(list,token_key)
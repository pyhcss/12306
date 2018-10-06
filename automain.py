# coding=utf-8

import time
from autologin import AutoLogin
from autoquery import AutoQuery
from autoorder import AutoOrder
from global_data import GLOBAL_QUERY_DATA as GQD
from global_data import GLOBAL_USERNAME,GLOBAL_PASSWORD


def main():
    autologin = AutoLogin()                     # 实例化登录模块
    rest = autologin.main(GLOBAL_USERNAME,GLOBAL_PASSWORD)# 执行登录
    if rest != "0":                             # 如果返回值不是0
        print rest                              # 打印错误信息
        return
    print "登录模块已完成"
    time.sleep(5)                               # 程序暂停5秒
    autoquery = AutoQuery()                     # 实例化查询模块
                                                # 从数据库查询信息并格式化数据
    format_data = autoquery.query_code(GQD["date"],GQD["from"],GQD["to"])
    while True:                                 # 死循环查询列车信息
        data = autoquery.get_info(format_data)  # 获取所有列车信息
                                                # 获取指定列车信息
        train_data = autoquery.query_train(GQD["train"],GQD["seattype"],data)
        if not train_data:
            print "相关列车暂无座位"
            time.sleep(5)
        else:
            break
    print train_data
    print "列车数据已获取 执行预定"
    time.sleep(3)
    autoorder = AutoOrder()                     # 实例化预定模块
    rest = autoorder.checklogin()               # 判断是否登录
    if rest != "0":
        print rest
        return                                  # 获取预定页面
    rest = autoorder.destine(train_data[0],GQD["date"],GQD["from"],GQD["to"])
    if rest != "0":
        print rest
        return
    token_key = autoorder.get_token()           # 获取token及key
    person_list = autoorder.get_person(GQD["person"])# 获取乘车人信息
    if not person_list[0]:
        print "乘车人不存在"
        return                                  # 发送乘车人请求 格式化乘车人信息字符串
    time.sleep(3)
    person_info = autoorder.order_person_submit(GQD["seattype"],person_list,token_key)
    if person_info == "seat error":
        print "没有相应座位"
        return                                  # 发送车次信息
    rest = autoorder.order_train_submit(GQD["date"],train_data,person_info,token_key)
    if rest != "0":
        print "车次提交失败"
        return
    time.sleep(3)                               # 最后提交预定信息
    rest = autoorder.order_submit(person_info,token_key,train_data)
    if rest != "0":
        print "订单提交失败"
        return
    rest = autoorder.queue_submit(token_key)    # 查询订单结果 返回结果
    if rest == "0":
        print "预定成功 请及时登录12306支付订单"


if __name__ == "__main__":
    main()

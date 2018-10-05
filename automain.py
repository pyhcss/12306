# coding=utf-8

import time
from autologin import AutoLogin
from autoquery import AutoQuery
from autoorder import AutoOrder
from global_data import GLOBAL_QUERY_DATA as GQD
from global_func import global_query_code


def query():
    """固定查询列车情况"""
    data = global_query_code(GQD["date"],GQD["from"],GQD["to"])
    data = AutoQuery().get_info(data)
    for i in data["data"]["result"]:
        data_list = i.split("|")
        for i in data_list:
            if GQD["train"].upper() in i:
                return data_list
    return []


def main():
    # autologin = AutoLogin()
    # rest = autologin.main()
    # if rest != "0":
    #     print rest
    # time.sleep(5)
    train_data = query()
    if not train_data[0]:
        print "列车暂无座位"
    else:
        autoorder = AutoOrder()
        # autoorder.checklogin()
        autoorder.destine(train_data[0],GQD["date"],GQD["from"],GQD["to"])
        # autoorder.get_token()


if __name__ == "__main__":
    main()

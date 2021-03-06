# coding=utf-8

# mysql数据库链接
GLOBAL_DB = {
    "host":"127.0.0.1", 
    "database":"kyfw_12306",
    "user":"root",
    "password":"",
    "charset":"utf8"
    }

# 查询相关
GLOBAL_QUERY_DATA = {
    "date":"2018-10-08",                          # 出发时间
    "from":"北京",                                 # 出发站
    "to":"天津",                                   # 目的站
    "train":["c2018"],                            # 列车号
    "person":["张三",],                            # 乘车人
    "seattype":"二等座",                           # 坐席类型
}

# 12306账户密码
GLOBAL_USERNAME = ""                              # 12306账号
GLOBAL_PASSWORD = ""                              # 12306密码

# 163邮箱相关om
GLOBAL_163 = {
    "to_mail":"",                                 # 收件方账号
    "from_mail":"",                               # 发件方账号
    "from_pwd":"",                                # 发件方密码
}

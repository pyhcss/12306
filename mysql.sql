create database kyfw_12306 charset="utf8";

create table station(
id int auto_increment primary key not null comment "车站id",
start_code varchar(10) not null comment "首字母编码",
name varchar(10) not null comment "名称",
name_code varchar(5) not null comment "正式编码三个大写字母",
pinyin varchar(32) not null comment "拼音",
start varchar(10) not null comment "首字母",
card_id int not null comment "网站中编号",
ctime datetime not null default current_timestamp comment "创建时间",
utime datetime not null default current_timestamp on update current_timestamp comment "更新时间",
isDelete boolean not null default false comment "是否删除",
index(name),
index(name_code)
) comment "车站代码表";
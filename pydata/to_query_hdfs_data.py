#!/bin/python
# coding: utf8

import sys
import os
import time
import datetime
import pymysql
import zlib
import json
import asyncio
# pyspark
import requests
from pyspark.sql import *
import pandas as pd



# database
MYSQL_HOST = ""
MYSQL_USER = ""
MYSQL_PASSWD = ""
MYSQL_DBNAME = ""
partition_num = 100  # mysql表数量

datacenter_conn = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    passwd=MYSQL_PASSWD,
    db=MYSQL_DBNAME,
    port=3306, charset='utf8mb4')
datacenter_conn.autocommit(True)

cursor = datacenter_conn.cursor()

spark = SparkSession.builder.getOrCreate()

# table name
table_list = [
    ("a", "a_part_%s", 32, 100),  # 分表1个
]

step_size = 10000

file_name_list = [
    ("h/%s/%s/%s", "./%s", "a",
     "h/%s/%s",
     ""),
]

# day 
days = [
]
# 如果days为空，days将会是昨天的日期
if not days:
    datadate = sys.argv[1]
    days.append(datadate)


# 从表名获取分表名
def get_table_format(table_name):
    for item in table_list:
        if table_name == item[0]:
            return item[1]
    raise Exception("table format not found!")


# 把数据插入表中
def dispatch_table(partition_format, cache_kv):
    sql2_1 = "insert into %s (bizuin, day, expand_field) values %s on duplicate key update expand_field=values(expand_field)"
    sql2_2 = " ({}, '{}', %s) "

    for key in cache_kv:
        if not cache_kv[key]:
            continue
        sql2_values = ""
        ex_list = []
        for one_record in cache_kv[key]:
            if sql2_values:
                sql2_values += ","
            sql2_values += sql2_2.format(one_record[0], one_record[1])
            ex_list.append(one_record[2])
        sql2 = sql2_1 % (partition_format % key, sql2_values)

        # 将hash后的数据写入对应分区
        cursor.execute(sql2, tuple(ex_list))

    return 0


# 检查分区是否存在，后续判断需要
def check_partition_exist(table_name, partition_name):
    """检查partition是否存在"""
    sql = """SELECT 
    TABLE_NAME, PARTITION_NAME 
    FROM information_schema.PARTITIONS 
    WHERE TABLE_NAME='%s' and PARTITION_NAME='%s' """ % (table_name, partition_name)
    cursor.execute(sql)
    one_row = cursor.fetchone()
    if not one_row:
        return False
    return True


# 创建新的分区
def create_new_partition(table_name, partition_name, target_str):
    sql = """ALTER TABLE %s ADD PARTITION (PARTITION %s VALUES IN (TO_DAYS('%s')))""" % (
    table_name, partition_name, str(target_str))
    cursor.execute(sql)
    datacenter_conn.commit()
    return


# 销毁旧的分区
def drop_old_partition(table_name, partition_name):
    sql = """alter table %s drop partition %s""" % (table_name, partition_name)
    cursor.execute(sql)
    datacenter_conn.commit()
    return


# 新分区命名
def make_partition_name(day):
    formatted_today = day.strftime('%Y%m%d')
    return "p" + formatted_today


# 获得日期
def get_offset_day(offset):
    today = datetime.date.today()
    return today - datetime.timedelta(days=offset)


# ==============================================================================================================================================================================================+


async def main():
    for tbl in table_list:
        # 名称，分表名，循环天数(分区数)，分表数
        _, table_name_format, day_range, pn = tbl[0], tbl[1], tbl[2], tbl[3]
        # 遍历每个分表
        for i in range(pn):
            table_name = table_name_format % i
            # 动态维护分区表
            for offset in range(5, -3, -1):
                today = get_offset_day(offset)
                # 创建新的分区
                partition_name = make_partition_name(today)
                print("will create partition_name:", partition_name)
                if not check_partition_exist(table_name, partition_name):
                    create_new_partition(table_name, partition_name, str(today))
                    print("partition created! named:", table_name, ".", partition_name)

                # 删除掉旧的分区
                day30ago = today - datetime.timedelta(days=day_range)
                partition_name = make_partition_name(day30ago)
                print("will del partition_name:", partition_name)
                if check_partition_exist(table_name, partition_name):
                    drop_old_partition(table_name, partition_name)
                    print("partition deleted! named:", table_name, ".", partition_name)

    # 改造 读取hdfs
    # 利用spark去获取的hdfs的信息
    for file_name in file_name_list:
        for ds in days:

            check_file = ds + ".check"

            check_file_address = file_name[0] % (file_name[2], ds, check_file)
            # 这里的参数header=True，本意是将首行作为列名，但同时也有 “跳过首行“的作用
            check_df = spark.read.csv(check_file_address, sep='\n', header=True)

            # 将 DataFrame 中的数据收集到本地列表
            check_data_list = check_df.collect()
            count = 0
            line_idx = 0
            for line in check_data_list:

                # 根据文件名去读实际的文件
                cache_kv = {i: [] for i in range(partition_num)}
                real_file_name = str(line[0])
                real_file_address = file_name[0] % (file_name[2], ds, real_file_name)

                df = spark.read.csv(real_file_address, sep='\t', header=False)
                total = df.count()
                if total == 0:
                    await AlarmHTTP(f"当前day:{ds},HDFS数据为空，请检查")
                    continue

                data_list = df.collect()
                for row in data_list:
                    try:
                        bizuin, day = int(row[0]), row[1]
                        expand_field_obj = json.loads(row[2])

                    except Exception as e:
                        await AlarmHTTP(f"json error: {e}  row ： {row} ")
                        continue

                    expand_field = zlib.compress(bytes(row[2], "utf-8"))
                    cache_kv[bizuin % partition_num].append((bizuin, day, expand_field))
                    if count and count % step_size == 0:
                        dispatch_table(get_table_format(file_name[2]), cache_kv)
                        cache_kv = {i: [] for i in range(partition_num)}

                    count += 1

                dispatch_table(get_table_format(file_name[2]), cache_kv)

                print("remove %s" % real_file_name)

            print("count:%s" % count)

    cursor.close()


if __name__ == '__main__':
    print("===================== begin ======================")
    print("----------- handle dispatch ------------")
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
        # asyncio.run("AlarmHTTP")

    print("===================== end ======================")

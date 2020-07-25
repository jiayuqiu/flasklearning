# coding:utf-8

"""
数据库连接

用到pandas与sqlachemy
"""

import time
# import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from pprint import pprint
import traceback
import sys
sys.path.append("./")

# from tools.YamlLoader import YamlLoader


def choose_db_conn(db_conn_df, mission_dict, mission_key):
    """
    根据任务信息，选择数据库链接

    :param db_conn_df: 数据库链接集合，dataframe
    :param mission_dict: 任务信息，dict
    :param mission_key: 任务key，str
    :return: sqlalchemy, db engine.
    """
    # 获取任务对应的数据库连接
    db_conn = db_conn_df[(db_conn_df["host"] == mission_dict[mission_key]["host"]) &
                         (db_conn_df["port"] == int(mission_dict[mission_key]["port"])) &
                         (db_conn_df["database"] == mission_dict[mission_key]["database"])]["db_engine"][0]
    return db_conn


def connect_engines(engine_info, ship_id):
    """
    根据配置文件中的

    :param engine_info: 数据库配置信息
    :param ship_id: ship编号
    :return: engine_dict, 存放数据库engine，字典
    """
    engine_dict = {}
    for _key in engine_info:
        _engine = ConnFactory(engine_info[_key], ship_id).make_conn().connect()
        engine_dict[_key] = _engine
    return engine_dict


class DBConnect:
    def __init__(self):
        self.sql_type = None
        self.user = None
        self.passwd = None
        self.host = None
        self.port = None
        self.database = None
        self.charset = "utf8"
    
    def get_type(self):
        return self.sql_type
    
    def connect(self):
        pass


class MySQLConn(DBConnect):
    def __init__(self, sql_type, user, passwd, host, port, database, charset="utf8"):
        self.sql_type = sql_type
        self.user = user
        self.passwd = passwd
        self.host = host
        self.port = port
        self.database = database
        self.charset = charset
    
    def connect(self):
        engine = create_engine(
            "mysql+pymysql://{user}:{passwd}@{host}:{port}/{database}?charset={charset}".format(
                user=self.user,
                passwd=self.passwd,
                host=self.host,
                port=self.port,
                database=self.database,
                charset=self.charset
            ),
            pool_recycle=7200
        )
        return engine


class PGConn(DBConnect):
    def __init__(self, sql_type, user, passwd, host, port, database, charset="utf8"):
        self.sql_type = sql_type
        self.user = user
        self.passwd = passwd
        self.host = host
        self.port = port
        self.database = database
        self.charset = charset
    
    def connect(self):
        engine = create_engine(
            "postgresql://{user}:{passwd}@{host}:{port}/{database}"
            .format(
                user=self.user,
                passwd=self.passwd,
                host=self.host,
                port=self.port,
                database=self.database,
                charset=self.charset
            ),
            pool_recycle=7200
        )
        return engine


class OracleConn(DBConnect):
    pass


class ConnFactory:
    """
    数据库连接工具
    """
    def __init__(self, conf_dict, ship_id):
        self.db_info_dcit = conf_dict
        self.ship_id = ship_id

    def make_conn(self):
        if self.db_info_dcit["sql_type"].lower() == "mysql":
            return MySQLConn(
                self.db_info_dcit["sql_type"], 
                self.db_info_dcit["user"], 
                self.db_info_dcit["password"], 
                self.db_info_dcit["host"], 
                self.db_info_dcit["port"], 
                self.db_info_dcit["database"].replace('{ship_id}', str(self.ship_id)), 
                self.db_info_dcit["charset"]
            )
        elif self.db_info_dcit["sql_type"].lower() == "pg":
            return PGConn(
                self.db_info_dcit["sql_type"], 
                self.db_info_dcit["user"], 
                self.db_info_dcit["password"], 
                self.db_info_dcit["host"], 
                self.db_info_dcit["port"], 
                self.db_info_dcit["database"].replace('{ship_id}', str(self.ship_id)), 
                self.db_info_dcit["charset"]
            )
        elif self.db_info_dcit["sql_type"].lower() == "oracle":
            print("暂时没有orcale数据库的连接功能")
            exit(1)
        else:
            print("请输入mysql;pg;oracle。")
            exit(1)


# def test():
    # conf_info = YamlLoader("/Users/highlander/PycharmProjects/dataclean/conf/config.yaml").get_dict()
    # engine_info = conf_info["engines"]
    # pprint(connect_engines(engine_info))
# 
# 
# test()

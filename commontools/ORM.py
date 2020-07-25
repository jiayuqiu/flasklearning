# coding:utf-8

import pandas as pd

from pprint import pprint

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sapg
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# from tools.YamlLoader import YamlLoader


Base = declarative_base()


GEN_ORM_TYPE_DICT = {
    "INTEGER": sa.INTEGER,
    "FLOAT": sa.FLOAT,
    "CHAR": sa.CHAR,
    "VARCHAR": sa.VARCHAR,
    "TEXT": sa.TEXT,
    "BLOB": sa.BLOB
}


PG_ORM_TYPE_DICT = {
    "INTEGER": sapg.INTEGER,
    "FLOAT": sapg.FLOAT,
    "CHAR": sapg.CHAR,
    "VARCHAR": sapg.VARCHAR,
    "TEXT": sapg.TEXT,
    "BLOB": sapg.BYTEA
}


class MakeOrmTable(object):
    """"""
    def __init__(self, table_info):
        self.name = table_info["name"]
        self.table_info = table_info

    @staticmethod
    def _make_mysql_column(name, columns_param):
        """"""
        type_ = columns_param["type"]

        if "primary_key" in columns_param.keys():
            # 该字段为主键
            primary_key = columns_param["primary_key"]

            # 增加判断是否自增:
            if "autoincrement" in columns_param.keys():
                autoincrement = columns_param["autoincrement"]
            else:
                autoincrement = False
        else:
            primary_key = False
            autoincrement = False

        return sa.Column(name=name, type_=GEN_ORM_TYPE_DICT[type_], autoincrement=autoincrement,
                         primary_key=primary_key)

    @staticmethod
    def _make_pg_column(name, columns_param):
        """"""
        type_ = columns_param["type"]

        if "primary_key" in columns_param.keys():
            # 该字段为主键
            primary_key = columns_param["primary_key"]

            # 增加判断是否自增:
            if "autoincrement" in columns_param.keys():
                autoincrement = columns_param["autoincrement"]
            else:
                autoincrement = False

            # 增加判断是否引用sequence
            if "sequence" in columns_param.keys():
                sequence = columns_param["sequence"]
            else:
                sequence = False

        else:
            primary_key = False
            autoincrement = False
            sequence = False

        # return sa.Column(name=name, type_=PG_ORM_TYPE_DICT[type_], autoincrement=autoincrement,
        #                  primary_key=primary_key)

        if sequence is False:
            return sa.Column(name=name, type_=PG_ORM_TYPE_DICT[type_], autoincrement=autoincrement,
                             primary_key=primary_key)
        else:
            return sa.Column(sa.Sequence(sequence), name=name, type_=PG_ORM_TYPE_DICT[type_],
                             autoincrement=autoincrement, primary_key=primary_key)

    def _get_column(self, sql_type, name, columns_param):
        """"""
        if sql_type == "mysql":
            return self._make_mysql_column(name, columns_param)
        elif sql_type == "pg":
            return self._make_pg_column(name, columns_param)

    def _make_base(self):
        """创建ORM基本类型BASE"""
        # 获取主键id的sequence
        id_columns = self.table_info["columns"]["id"]

        class TableBase(Base):
            __tablename__ = self.name

            id = self._get_column(
                sql_type=self.table_info["engine"]["sql_type"],
                name="id",
                columns_param=id_columns
            )

        # 根据table配置信息，动态添加字段
        table_columns_dict = self.table_info["columns"]
        for _col in [c for c in table_columns_dict.keys() if c != "id"]:
            _Column = self._get_column(
                sql_type=self.table_info["engine"]["sql_type"],
                name=_col,
                columns_param=table_columns_dict[_col]
            )
            setattr(TableBase, _col, _Column)

        return TableBase

    def to_class(self):
        """
        返回一个base class

        :return:
        """
        return self._make_base()


# if __name__ == "__main__":
#     engine = sa.create_engine("mysql+pymysql://developer:highLANDER@2017@192.168.1.188/tempdb")
#     DBsession = sessionmaker(bind=engine)  # 创建与数据库的会话session class ,注意,这里返回给session的是个class,不是实例
#     session = DBsession()  # 生成session实例

#     minfo = YamlLoader("/Users/highlander/PycharmProjects/DBInsert/conf/ship1.yaml").get_dict()

#     for tab_name in minfo["tables"]:
#         org_base = MakeOrmTable(tab_name).to_class()
#         print(org_base)

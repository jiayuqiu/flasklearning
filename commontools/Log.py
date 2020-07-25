# coding:utf-8

import logging
import re
import time
import os
import numpy as np

from pprint import pprint
from logging.handlers import TimedRotatingFileHandler


class DBLogger:
    """日志类"""
    def __init__(self, log_name, log_level=logging.INFO):
        """初始化logger信息"""
        # 日志输出格式
        log_fmt = '%(asctime)s\tFile \"%(filename)s\",line %(lineno)s\t%(levelname)s: %(message)s'
        formatter = logging.Formatter(log_fmt)

        # 创建日志输出路径
        file_path = '/' + os.path.join(*log_name.split("/")[:-1])

        if not os.path.exists(file_path):
            os.makedirs(file_path)

        # 设置文件日志
        log_file_handler = TimedRotatingFileHandler(
            filename=log_name,
            when="D",
            interval=1,
            backupCount=7
        )
        log_file_handler.suffix = "%Y-%m-%d.log"
        log_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
        log_file_handler.setFormatter(formatter)
        # log_file_handler.setLevel(log_level)
        self.logger = logging.getLogger()
        self.logger.addHandler(log_file_handler)

        console = logging.StreamHandler()
        console.setFormatter(formatter)
        self.logger.addHandler(console)
        self.logger.setLevel(log_level)


class LoggerFactory:
    def __init__(self, log_path, app_info, log_level=logging.INFO):
        # 日志路径
        self.log_path = log_path

        # 应用配置信息
        self.app_info = app_info

        # 日志登记
        self.log_level = log_level

    def make_one(self, table_info):
        """构建单个任务对应的日志功能"""
        log_path = self.log_path
        tb_engine_info = table_info["engine"]

        host = tb_engine_info["host"]
        sql_type = tb_engine_info["sql_type"]
        port = str(tb_engine_info["port"])
        db = tb_engine_info["database"]
        tb_name = table_info["name"]

        # 创建该任务对应的日志功能
        log_full_path = os.path.join(log_path, host, port, db, tb_name + ".log")
        _logger = DBLogger(
            log_name=log_full_path,
            log_level=self.log_level
        )
        return _logger
    
    def make_all(self):
        """构建不同任务对应的日志功能"""
        loggers_dict = {}
        tables_info = self.app_info['tables']

        for info_key in tables_info:
            _logger = self.make_one(tables_info[info_key])
            loggers_dict[info_key] = _logger

        return loggers_dict

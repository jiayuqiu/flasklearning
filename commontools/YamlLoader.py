# coding:utf-8

"""
yaml配置文件读取工具

输出为dict
"""

import yaml


class YamlLoader:
    def __init__(self, yaml_full_path):
        f = open(yaml_full_path, "r")
        self.__db_conf = yaml.load(f)
        f.close()
    
    def get_dict(self):
        """获得yaml的数据"""
        return self.__db_conf

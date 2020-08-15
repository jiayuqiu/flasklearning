#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   register.py
@Time    :   2020/08/07 11:38:49
@Author  :   Qiu Jiayu
@Version :   1.0
@Contact :   qiujy@whbluewhale.com
@Desc    :   zookeeper服务注册
'''

# here put the import lib
from kazoo.client import KazooClient
import time
import json
import os


class Register(object):
    def __init__(self, zk_host, zk_port):
        self.__zk = KazooClient(hosts=f'{zk_host}:{zk_port}')

    def register_node(self, server_info, fpath, fname):
        """注册单节点服务

        Args:
            server_info ([dict]): [api的host与port信息]
            fpath ([string]): [服务路径]
            fname ([string]): [服务名称]
        """
        # connect zookeeper client
        self.__zk.start()

        # register mircoservers
        print(f"fpath = {fpath}")
        self.__zk.ensure_path(fpath)
        value = json.dumps(server_info)
        self.__zk.create(os.path.join(fpath, fname), value.encode(), sequence=True)
        self.__zk.stop()

    def register_nodes(self, server_info_list, fpath, fname):
        """注册多节点服务

        Args:
            server_info_list ([list]]): [多服务器的host与port信息]
            fpath ([string]): [服务路径]
            fname ([string]): [服务名称]
        """
        # connect zookeeper client
        self.__zk.start()

        # register mircoservers
        print(f"fpath = {fpath}")
        self.__zk.ensure_path(fpath)
        for _, server_info in enumerate(server_info_list):
            value = json.dumps(server_info)
            self.__zk.create(os.path.join(fpath, fname), value.encode(), sequence=True)
        self.__zk.stop()


def main():
    # register one node
    reg = Register(zk_host="192.168.7.239", zk_port=2181)
    reg.register_node(
        server_info={"host": "192.168.7.209", "port": 18888},
        fpath="/services/alg",
        fname="weather_clf"
    )
    print("reg finish.")


if __name__ == "__main__":
    main()

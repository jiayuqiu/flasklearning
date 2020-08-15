#coding=utf-8
from kazoo.client import KazooClient
import time
import json


zk = KazooClient(hosts='192.168.7.239:2181')
zk.start()

# def test_ensure():
#     zk.ensure_path('/macs')
 
def test_create():
    nodename = '/macs/weather_clf'
    zk.ensure_path('/macs')
    value = json.dumps({'host': "192.168.6.84", 'port': 8888})

    zk.create(nodename, value.encode(), ephemeral=True, sequence=True)

if __name__ == '__main__':
    # zk.delete('/kwsy')
    test_create()
    input(" ------------ ")
    zk.stop()

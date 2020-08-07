from kazoo.client import KazooClient
import json

zk_client = KazooClient(hosts='192.168.7.239:2181')
zk_client.start()

path = '/macs/'
node_list = zk_client.get_children('/macs')
print(node_list, type(node_list))

zookeeper_servers = list()
for _, node in enumerate(node_list):
    zookeeper_servers.append(path + node)
print(zookeeper_servers)

node_data_list = list()
for _, server in enumerate(zookeeper_servers):
    data_info = zk_client.get(server)[0]
    api_dict = json.loads(data_info)
    node_data_list.append(api_dict)

print(node_data_list)
node_dict = node_data_list[0]
zk_client.stop()

# import socket
import requests

url = f"http://{node_dict['host']}:{node_dict['port']}/weather_clf/classify?wind_speed=19.9&wave_height=1.25"
print(url)

res = requests.get(url)
print(res.text)

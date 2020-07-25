#! anaconda python
# -*- coding:utf-8 -*-
# 作者：邱家瑜
# 创建：2020-06-12
# 更新：2020-06-12
# 用意：用于海况分类参数信息


# 风力等级 - 风速(m/s)对应关系
WIND_LEVEL_SPEED = {
    0: {'min': 0.0, 'max': 0.2},
    1: {'min': 0.3, 'max': 1.5},
    2: {'min': 1.5, 'max': 3.3},
    3: {'min': 3.3, 'max': 5.4},
    4: {'min': 5.4, 'max': 7.9},
    5: {'min': 7.9, 'max': 10.7},
    6: {'min': 10.7, 'max': 13.8},
    7: {'min': 13.8, 'max': 17.1},
    8: {'min': 17.1, 'max': 20.7},
    9: {'min': 20.7, 'max': 24.4},
    10: {'min': 24.4, 'max': 28.4},
    11: {'min': 28.4, 'max': 32.6},
    12: {'min': 32.6, 'max': 36.9}
}

# 海况分类表
SEA_STATE_DICT = {
    0: {'wave_height': {'min': 0.0, 'max': 0.0}, 'wind_level': {'min': 0, 'max': 0}},
    1: {'wave_height': {'min': 0.0, 'max': 0.1}, 'wind_level': {'min': 1, 'max': 1}},
    2: {'wave_height': {'min': 0.1, 'max': 0.5}, 'wind_level': {'min': 2, 'max': 2}},
    3: {'wave_height': {'min': 0.5, 'max': 1.25}, 'wind_level': {'min': 3, 'max': 4}},
    4: {'wave_height': {'min': 1.25, 'max': 2.5}, 'wind_level': {'min': 5, 'max': 5}},
    5: {'wave_height': {'min': 2.5, 'max': 4.0}, 'wind_level': {'min': 6, 'max': 6}},
    6: {'wave_height': {'min': 4.0, 'max': 6.0}, 'wind_level': {'min': 7, 'max': 7}},
    7: {'wave_height': {'min': 6.0, 'max': 9.0}, 'wind_level': {'min': 8, 'max': 9}},
    8: {'wave_height': {'min': 9.0, 'max': 14.0}, 'wind_level': {'min': 10, 'max': 17}},
    9: {'wave_height': {'min': 14.0, 'max': 99.9}, 'wind_level': {'min': 17, 'max': 99}}
}

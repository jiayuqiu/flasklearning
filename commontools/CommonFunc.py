# coding:utf-8

import numpy as np
import pandas as np


def is_number(s):
    """判断字符串是否为数字

    Arguments:
        s {[str]} -- [input string]

    Returns:
        [bool] -- [True or False]
    """
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def convert_coor(lon_lat):
    """导航中国际标准经纬度格式转换

    国际标准中，经纬度格式为：9900.2451171875，个位数中从十位数后为分，从百位数前为度。
    格式说明：ddmm.mmmm，表示dd°mm.mmmm′

    东 ： ＋，西 ： －
    北 ： ＋，南 ： －

    Arguments:
        lon_lat {[float]} -- [标准格式数值]

    Returns:
        [float] -- [转换为十分位数的数值]
    """
    if lon_lat < 0:
        b = -1
    else:
        b = 1

    value = abs(lon_lat)

    f = value // 100
    a = value % 100

    c_v = (f + a / 60) * b
    return float(format(c_v,'.6f'))

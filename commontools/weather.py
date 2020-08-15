#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from scipy.interpolate import interp1d, interp2d

MIN_TIMESTAMP = 1506776400  # 气象数据记录的最小时间戳
MAX_TIMESTAMP = 1577926800  # 气象数据记录的最大时间戳

weather_engine = create_engine("mysql+pymysql://root:Root@123@192.168.7.209:13306/weather")


def cal_timestamp(current_timestamp):
    """计算前后时间戳

    Arg:
         current_timestamp - 特征库工况记录对应的时间戳

    Returns:
         (prev_timestamp, next_timestamp) - 当前时间戳对应的标准气象数据前后时间戳，超出范围则返回 None

    """
    # 如果 current_timestamp 超出范围，返回 None
    if current_timestamp > MAX_TIMESTAMP or current_timestamp < MIN_TIMESTAMP:
        return None

    # 如果 current_timestamp 刚好与标准气象时间戳匹配，直接返回 current_timestamp
    elif (current_timestamp - MIN_TIMESTAMP) % 10800 == 0:
        return current_timestamp, current_timestamp

    # 如果 current_timestamp 在标准气象时间戳间隔内，则计算其前后的气象标准时间戳
    else:
        cnt = (current_timestamp - MIN_TIMESTAMP) // 10800
        return MIN_TIMESTAMP + 10800 * cnt, MIN_TIMESTAMP + 10800 * (cnt + 1)


def cal_lnglat(current_lng, current_lat):
    """计算附近的经纬度方格

    Args:
        current_lng - 当前经度
        current_lat - 当前纬度

    Returns:
        (west_lng, east_lng, south_lat, north_lat) - 围绕当前经纬度的经纬度方格
    """

    west_lng, east_lng, north_lat, south_lat = None, None, None, None

    # 如果超出经纬度范围
    if current_lng > 180 or current_lng < -180 or current_lat > 85 or current_lat < -85:
        return None

    # 如果经纬度刚好为整数
    if int(current_lng) == current_lng:
        west_lng, east_lng = current_lng, current_lng

    if int(current_lat) == current_lat:
        north_lat, south_lat = current_lat, current_lat

    # 经纬度不为整数且在范围内
    west_lng, east_lng = math.floor(current_lng), math.ceil(current_lng)
    south_lat, north_lat = math.floor(current_lat), math.ceil(current_lat)

    return west_lng, east_lng, south_lat, north_lat


# 招商船经纬度转换
def latProcess(lat):
    latStr = str(lat)
    nega = 0
    if latStr[0] == "-":
        nega = 1
        latStr = latStr[1:]

    latInt = int(float(latStr))
    latIntStr = str(latInt)

    cutPlace = len(latIntStr) - 2
    if cutPlace < 0:
        cutPlace = 0

    degree = latStr[0:cutPlace]
    minu = latStr[cutPlace:]
    if degree == "0." or degree == "":
        degree = 0
    res = int(degree) + (float(minu)/60)
    res = float(format(res,'.3f'))
    if nega == 1:
        res = res * (-1)
    return res


def func(engine):
    """ 返回根据经纬度、时间戳查询气象数据并做预处理的函数

    Arg:
        engine - sqlalchemy engine

    Return:
        query_weather - 查询气象函数
    """
    def query_weather(lng, lat, timestamp):
        """ 根据经纬度、时间戳查询原始气象数据，并做预处理

        Args:
            lng - 经度
            lat - 纬度
            timestamp - 时间戳

        Return:
            df - 气象数据记录均值 DataFrame，存在空值则返回 None
        """
        df = pd.read_sql(f"select `current_magnitude`, `current_direction`, `wind_magnitude`, `wind_direction`,"
                         f"`wave_height`, `wave_period`, `wave_direction`, `swell_height`, `swell_period`, "
                         f"`swell_direction`, `surface_pressure`, `surface_temperature`, `500mB_height` "
                         f"from weather where longitude={lng} and latitude={lat} and timestamp={timestamp}",
                         con=engine)

        df['current_magnitude'].replace(-99, np.nan, inplace=True)
        df['current_direction'].replace(-999, np.nan, inplace=True)
        df['wind_magnitude'].replace(-999, np.nan, inplace=True)
        df['wind_direction'].replace(-999, np.nan, inplace=True)
        df['wave_height'].replace(-99, np.nan, inplace=True)
        df['wave_period'].replace(-99, np.nan, inplace=True)
        df['wave_direction'].replace(-999, np.nan, inplace=True)
        df['swell_height'].replace(-99, np.nan, inplace=True)
        df['swell_period'].replace(-99, np.nan, inplace=True)
        df['swell_direction'].replace(-999, np.nan, inplace=True)
        df['surface_pressure'].replace(-999999, np.nan, inplace=True)
        df['surface_temperature'].replace(-99, np.nan, inplace=True)
        df['500mB_height'].replace(-99999, np.nan, inplace=True)

        return df.mean()

    return query_weather


FEATURES_NUM = 13  # 气象数据特征数量
query_weather = func(weather_engine)


def generate_weather_data(current_lng, current_lat, current_timestamp):
    """ 根据特征库记录对应的经纬度、时间戳查询并计算气象数据

    Args:
        current_lng - 特征库中记录的经度
        current_lat - 特征库中记录的纬度
        current_timestamp - 特征库对应的 prev_timestamp

    Returns:
        res_row - 计算得到的气象数据数组 np.array，目前计算中出现查询超出范围或者原始气象数据存在空值的情况返回 None
    """
    current_lng, current_lat = latProcess(current_lng), latProcess(current_lat)
    generate_lnglat = cal_lnglat(current_lng, current_lat)
    generate_timestamp = cal_timestamp(current_timestamp)

    # 如果经纬度或者时间戳超出范围，则不予处理
    if generate_lnglat is None or generate_timestamp is None:
        return None

    west_lng, east_lng, south_lat, north_lat = generate_lnglat
    prev_timestamp, next_timestamp = generate_timestamp

    res_row = np.zeros(FEATURES_NUM)

    # 如果current_timestamp刚好与气象数据时间戳相同
    if prev_timestamp == next_timestamp:
        # 1. current_lng 刚好与气象数据经度相同，且 current_lat 与气象数据纬度不同 - 纬度方向一维插值
        if west_lng == east_lng and south_lat != north_lat:
            # 查询纬度相关气象数据进行插值
            south_weather = query_weather(current_lng, south_lat, current_timestamp)
            north_weather = query_weather(current_lng, north_lat, current_timestamp)

            for idx in range(FEATURES_NUM):
                south_value, north_value = south_weather[idx], north_weather[idx]

                if math.isnan(south_value) or math.isnan(north_value):
                    res_row[idx] = np.nanmean([south_value, north_value])
                else:
                    x = np.array([south_lat, north_lat])
                    y = np.array([south_value, north_value])
                    res_row[idx] = interp1d(x, y)(current_lat)

        # 2. current_lng 与气象数据经度不同， 且 current_lat 与气象数据纬度相同 - 经度方向一维插值
        if west_lng != east_lng and south_lat == north_lat:
            # 查询经度相关气象数据进行插值
            west_weather = query_weather(west_lng, current_lat, current_timestamp)
            east_weather = query_weather(east_lng, current_lat, current_timestamp)

            for idx in range(FEATURES_NUM):
                west_value, east_value = west_weather[idx], east_weather[idx]

                if math.isnan(west_value) or math.isnan(east_value):
                    res_row[idx] = np.nanmean([west_value, east_value])
                else:
                    x = np.array([west_lng, east_lng])
                    y = np.array([west_value, east_value])
                    res_row[idx] = interp1d(x, y)(current_lng)

        # 3. current_lng 与气象数据经度相同， 且 current_lat 与气象数据纬度相同 - 直接返回气象数据即可
        if west_lng == east_lng and south_lat == north_lat:
            weather = query_weather(current_lng, current_lat, current_timestamp)
            res_row = np.array(weather)

        # 4. current_lng 与气象数据经度不同， 且 current_lat 与气象数据纬度不同 - 二维插值
        if west_lng != east_lng and south_lat != north_lat:
            # 查询经纬度相关的气象数据
            west_south_weather = query_weather(west_lng, south_lat, current_timestamp)
            west_north_weather = query_weather(west_lng, north_lat, current_timestamp)
            east_south_weather = query_weather(east_lng, south_lat, current_timestamp)
            east_north_weather = query_weather(east_lng, north_lat, current_timestamp)

            for idx in range(FEATURES_NUM):
                west_south_value, west_north_value = west_south_weather[idx], west_north_weather[idx]
                east_south_value, east_north_value = east_south_weather[idx], east_north_weather[idx]

                if math.isnan(west_south_value) or math.isnan(west_north_value) or math.isnan(east_south_value) or math.isnan(east_north_value):
                    res_row[idx] = np.nanmean([west_south_value, west_north_value, east_south_value, east_north_value])
                else:
                    grid_x, grid_y = np.meshgrid([west_lng, east_lng], [south_lat, north_lat])
                    z = np.array([[west_south_weather[idx], east_south_weather[idx]],
                              [west_north_weather[idx], east_north_weather[idx]]])
                    res_row[idx] = interp2d(grid_x, grid_y, z)(current_lng, current_lat)

    # 如果 current_timestamp 与气象数据时间戳不同
    else:
        # 1. current_lng 刚好与气象数据经度相同，且 current_lat 与气象数据纬度不同
        if west_lng == east_lng and south_lat != north_lat:
            # 查询时间-纬度相关的气象数据
            prev_south_weather = query_weather(current_lng, south_lat, prev_timestamp)
            prev_north_weather = query_weather(current_lng, north_lat, prev_timestamp)
            next_south_weather = query_weather(current_lng, south_lat, next_timestamp)
            next_north_weather = query_weather(current_lng, north_lat, next_timestamp)

            for idx in range(FEATURES_NUM):
                prev_south_value, prev_north_value = prev_south_weather[idx], prev_north_weather[idx]
                next_south_value, next_north_value = next_south_weather[idx], next_north_weather[idx]

                if math.isnan(prev_south_value) or math.isnan(prev_north_value) or math.isnan(next_south_value) or math.isnan(next_north_value):
                    res_row[idx] = np.nanmean([prev_south_value, prev_north_value, next_south_value, next_south_value])
                else:
                    grid_x, grid_y = np.meshgrid([south_lat, north_lat], [prev_timestamp, next_timestamp])
                    z = np.array([[prev_south_weather[idx], prev_north_weather[idx]],
                                [next_south_weather[idx], next_north_weather[idx]]])
                    res_row[idx] = interp2d(grid_x, grid_y, z)(current_lat, current_timestamp)

        # 2. current_lng 与气象数据经度不同， 且 current_lat 与气象数据纬度相同
        if west_lng != east_lng and south_lat == north_lat:
            # 查询时间-经度相关的气象数据
            prev_west_weather = query_weather(west_lng, current_lat, prev_timestamp)
            prev_east_weather = query_weather(east_lng, current_lat, prev_timestamp)
            next_west_weather = query_weather(west_lng, current_lat, next_timestamp)
            next_east_weather = query_weather(east_lng, current_lat, next_timestamp)

            for idx in range(FEATURES_NUM):
                prev_west_value, prev_east_value = prev_west_weather[idx], prev_east_weather[idx]
                next_west_value, next_east_value = next_west_weather[idx], next_east_weather[idx]

                if math.isnan(prev_west_value) or math.isnan(prev_east_value) or math.isnan(next_west_value) or math.isnan(next_east_value):
                    res_row[idx] = np.nanmean([prev_west_value, prev_east_value, next_west_value, next_east_value])
                else:
                    grid_x, grid_y = np.meshgrid([west_lng, east_lng], [prev_timestamp, next_timestamp])
                    z = np.array([[prev_west_weather[idx], prev_east_weather[idx]],
                                    [next_west_weather[idx], next_east_weather[idx]]])
                    res_row[idx] = interp2d(grid_x, grid_y, z)(current_lng, current_timestamp)

        # 3. current_lng 与气象数据经度相同， 且 current_lat 与气象数据纬度相同
        if west_lng == east_lng and south_lat == north_lat:
            # 查询时间相关的气象数据
            prev_weather = query_weather(current_lng, current_lat, prev_timestamp)
            next_weather = query_weather(current_lng, current_lat, next_timestamp)

            for idx in range(FEATURES_NUM):
                prev_value, next_value = prev_weather[idx], next_weather[idx]

                if math.isnan(prev_value) or math.isnan(next_value):
                    res_row[idx] = np.nanmean([prev_value, next_value])
                else:
                    x = np.array([prev_timestamp, next_timestamp])
                    y = np.array([prev_weather[idx], next_weather[idx]])
                    res_row[idx] = interp1d(x, y)(current_timestamp)

        # 4. current_lng 与气象数据经度不同， 且 current_lat 与气象数据纬度不同
        if west_lng != east_lng and south_lat != north_lat:
            # 查询时间-经度-纬度相关的气象数据
            prev_west_south_weather = query_weather(west_lng, south_lat, prev_timestamp)
            prev_west_north_weather = query_weather(west_lng, north_lat, prev_timestamp)
            prev_east_south_weather = query_weather(east_lng, south_lat, prev_timestamp)
            prev_east_north_weather = query_weather(east_lng, north_lat, prev_timestamp)
            next_west_south_weather = query_weather(west_lng, south_lat, next_timestamp)
            next_west_north_weather = query_weather(west_lng, north_lat, next_timestamp)
            next_east_south_weather = query_weather(east_lng, south_lat, next_timestamp)
            next_east_north_weather = query_weather(east_lng, north_lat, next_timestamp)

            # prev_timestamp 插值
            grid_x, grid_y = np.meshgrid([west_lng, east_lng], [south_lat, north_lat])

            for idx in range(FEATURES_NUM):
                # prev_timestamp、next_timestamp 分别根据经纬度进行二维插值

                # prev 平面插值
                prev_west_south_value, prev_east_south_value = prev_west_south_weather[idx], prev_east_south_weather[idx]
                prev_west_north_value, prev_east_north_value = prev_west_north_weather[idx], prev_east_north_weather[idx]

                if math.isnan(prev_west_south_value) or math.isnan(prev_east_south_value) or \
                        math.isnan(prev_west_north_value) or math.isnan(prev_east_north_value):
                    prev_curr_z = np.nanmean([prev_west_south_value, prev_east_south_value,
                                              prev_west_north_value, prev_east_north_value]).reshape(1)
                    
                else:
                    prev_z = np.array([[prev_west_south_value, prev_east_south_value],
                                       [prev_west_north_value, prev_east_north_value]])
                    prev_curr_z = interp2d(grid_x, grid_y, prev_z)(current_lng, current_lat)

                # next 平面插值
                next_west_south_value, next_east_south_value = next_west_south_weather[idx], next_east_south_weather[idx]
                next_west_north_value, next_east_north_value = next_west_north_weather[idx], next_east_north_weather[idx]

                if math.isnan(next_west_south_value) or math.isnan(next_east_north_value) or \
                        math.isnan(next_west_north_value) or math.isnan(next_east_north_value):
                    next_curr_z = np.nanmean([next_west_south_value, next_east_south_value,
                                              next_west_north_value, next_east_north_value]).reshape(1)
                    
                else:
                    next_z = np.array([[next_west_south_value, next_east_south_value],
                                       [next_west_north_value, next_east_north_value]])
                    next_curr_z = interp2d(grid_x, grid_y, next_z)(current_lng, current_lat)

                # 基于时间戳再进行一维插值
                if math.isnan(prev_curr_z) or math.isnan(next_curr_z):
                    res_row[idx] = np.nanmean([prev_curr_z, next_curr_z])
                else:
                    x = np.array([prev_timestamp, next_timestamp])
                    y = np.concatenate([prev_curr_z, next_curr_z])
                    res_row[idx] = interp1d(x, y)(current_timestamp)

    return res_row


if __name__ == "__main__":
    res_row = generate_weather_data(31.2999992370605, 0, 1550806020)
    print(res_row)
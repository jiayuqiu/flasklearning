# coding:utf-8

import pandas as pd
import numpy as np
import io

from io import BytesIO
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from commontools.DC import DeColor, ColorData


def img2bytes(img):
    """将img转换为bytes"""
    roiImg = img.crop()

    imgByteArr = io.BytesIO()
    roiImg.save(imgByteArr, format="png")
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr


def check_png(img, dim):
    """
    判断配置文件中的png配置是否与接收的png格式相同

    :param img: 图片
    :param dim: 配置文件中的维度
    :return:
    """
    # 获取图片的维度
    weight, height, m = np.array(img).shape

    if weight != height:
        # 若图片的长宽不等，则报错
        raise("若图片的长宽不等")
    else:
        # 若图片长度相等，则判断是否与配置的维度相同
        if weight != dim:
            raise ("若图片的维度与配置的维度不等")
    return True


class HLDBytes:
    def __init__(self, data_bytes, png_conf):
        # 设置二进制数据
        self.data = data_bytes
        self.png_conf = png_conf

    def to_cd(self):
        """
        将二进制数据转换为cd

        :return:
        """
        buffer = BytesIO()
        buffer.write(self.data)
        cd = ColorData(Image.open(buffer))
        return cd

    def to_img(self):
        """
        将二进制数据转换为img

        :param orderkey_df:
        :return:
        """
        buffer = BytesIO()
        buffer.write(self.data)
        cd = ColorData(Image.open(buffer))
        return cd.img

    def get_value_from_cd(self, cd, orderid, keyname):
        """从cd中获取数值"""
        key_int = int(keyname)
        if (key_int >= -500000) & (key_int <= -500029):
            # 解析ais数据
            _t = "ais"
            if orderid < 0:
                # 解析字符串数据
                _v = cd.getString(self.png_conf["dim"] + orderid - self.png_conf["reserverow"])
            else:
                # 解析数值型数据
                _v = cd.getValue(orderid - 1)
        else:
            # 解析其他项数据
            _t = "other"
            _v = _v = cd.getValue(orderid - 1)

        # 返回数值、类型
        return keyname, _v, _t

    def to_json(self, orderkey_df):
        """
        将二进制数据转换为规定格式的json

        json emample:
        {

          "utc": 1558675710,

          "ais": {"mmsi": 413364630(int),

             "status": 0(int),

             "lat": 31.14569(double，单位：度，合理区间：(-89.9, 90.0)),

             "lon": 121.90348(double，单位：度，合理区间：(-179.9, 180.0)),

             "sog": 11.1(double，单位：节),

             "cog": 302.9(double，单位：度/秒，合理区间：(0-359.9)),

             "hdg": 300(double，单位：度，合理区间：(0-359.9)),

             "rot": 0.0(double, 单位：未知，合理区间：(-127, 127)),

             "callSign", BKWT6(varchar),

             "eta": yyyy-mm-dd HH:MM:SS,

             "dest": Shanghai},

          "other": {"a":123, "b":123}

        }

        :param orderke_df:
        :return:
        """
        cd = self.to_cd()

        # 判断配置文件中的png配置是否与接收的png格式相同
        check_png(cd.img, self.png_conf["dim"])

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = list()  # 初始化任务列表
            _d = {"ais": {}, "other": {}}  # 初始化解析结果

            # 1. 添加utc
            _d["utc"] = cd.getValue(0, 0)

            # 2. 添加ais与other计算任务
            for orderid, keyname in zip(orderkey_df["orderid"], orderkey_df["keyname"]):
                futures.append(executor.submit(self.get_value_from_cd, cd, orderid, keyname))

            # 3. 等待计算完成
            for future in as_completed(futures):
                cd_keyname, cd_v, cd_t = future.result()
                _d[cd_t][cd_keyname] = cd_v
        return _d

    def to_dataframe(self, orderkey_df):
        """
        将二进制数据转换为dataframe，格式为record_engine
        df.columns = ["UTC", "device_name", "per", "value", "unit", "is_warnning", "shipid"]

        :param orderkey_df:
        :return:
        """
        # 二进制图片数据转为
        buffer = BytesIO()
        buffer.write(self.data)
        cd = ColorData(Image.open(buffer))

        utc = cd.getValue(0, 0)

        engine_list = list()
        for orderkey, KeyValue in zip(orderkey_df["orderkey"], orderkey_df["KeyValue"]):
            engine_list.append([utc, KeyValue, 0, cd.getValue(orderkey - 1), 0, 0, 7])
        engine_df = pd.DataFrame(engine_list,
                                 columns=["UTC", "device_name", "per", "value", "unit", "is_warnning", "shipid"])
        return engine_df


class HLDEngine:
    def __init__(self, utc_engine_df):
        # 记录engine数据
        self.engine_df = utc_engine_df

    def to_img(self, utc, orderkey_df, weight, height, sort_version, png_version, png_mode="RGB"):
        """
        转换会img

        :param utc:
        :param orderkey_df:
        :param weight:
        :param height:
        :param sort_version:
        :param png_version:
        :param png_mode:
        :return:
        """
        utc_img = Image.new(png_mode, (weight, height), 0)
        utc_cd = ColorData(utc_img)
        utc_cd.setValue(0, utc, 0)
        utc_cd.setValue(1, sort_version)
        utc_cd.setValue(2, png_version)

        # 将每个工况点数据放入png
        for idx, row in self.engine_df.iterrows():
            _v = row["value"]
            _keyvalue = row["DEVICE_NAME"]
            keyvalue_match_res = orderkey_df[orderkey_df["KeyValue"] == _keyvalue]["orderkey"]

            if len(keyvalue_match_res) > 0:
                _orderkey = keyvalue_match_res.values[0]
                utc_cd.setValue(_orderkey - 1, row["value"])
        return utc_cd.img

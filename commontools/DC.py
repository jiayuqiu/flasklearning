# coding=utf-8

"""update time: 20190628"""

import traceback
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import re


class DBLogger:
    """日志类"""
    def __init__(self, log_name, log_level=logging.DEBUG):
        """初始化logger信息"""
        # 日志输出格式
        log_fmt = '%(asctime)s\tFile \"%(filename)s\",line %(lineno)s\t%(levelname)s: %(message)s'
        formatter = logging.Formatter(log_fmt)

        # 创建日志输出路径
        file_path = os.path.join(*log_name.split("/")[:-1])

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


class DeColor:
    """
        Decolor 转换数值为RGB颜色，隐藏数据到图片中。
        可处理的数值范围为 0 ~ 0xFFFFFFFFFFFFFFFF

        可通过 option['type'] 指定 单精度float，或双精度double
        对应的是单像素和双像素
    """

    def __init__(self, option={'type': 'double'}):
        self.option = option
        if self.option['type'] == 'double':
            self.len_exponent = 11
            self.len_fraction = 52
            self.Zero = 0xFFFFFFFFFFFFFFFF
            self.NullColor = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
        else:
            self.len_exponent = 8
            self.len_fraction = 23
            self.Zero = 0xFFFFFFFF
            self.NullColor = [(0, 0, 0), (0, 0, 0)]

        self.move_exponent = (1 << (self.len_exponent - 1)) - 1
        self.mask_exponent = ((1 << self.len_exponent) - 1) << self.len_fraction
        self.mask_fraction = (1 << self.len_fraction) - 1
        self.total_len = self.len_exponent + self.len_fraction

    def encodeStr(self, width, str=None):
        # print(width)
        if str is None:
            return self.NullColor

        def _estr(i):
            if i >= len(str):
                return 255
            return ord(str[i])

        cols = []
        if len(str) < width:
            for i in range(0, len(str) + 1, 3):
                cols.append((_estr(i), _estr(i + 1), _estr(i + 2)))
        else:
            # print("string length is larger than png width")
            logger = DBLogger('./logs/dc.log')
            logger.logger.warning("string length is larger than png width")
            for i in range(0, width, 3):
                cols.append((_estr(i), _estr(i + 1), _estr(i + 2)))

        return cols

    def decodeStr(self, colors):
        if colors == self.NullColor:
            return None

        def _dstr(v):
            if v > 126:
                return ''
            return chr(v)

        str = ""
        for i in range(len(colors)):
            c1 = _dstr(colors[i][0])
            c2 = _dstr(colors[i][1])
            c3 = _dstr(colors[i][2])
            str += c1 + c2 + c3
            if(c1=='' or c2=='' or c3==''):
                break
        return str

    def encode(self, value=None):
        if value is None:
            return self.NullColor
        bits = self.toBits_IEEE754(value)
        if self.option['type'] == 'double':
            c0 = (bits & 0xFF00000000000000) >> 56
            c1 = (bits & 0x00FF000000000000) >> 48
            c2 = (bits & 0x0000FF0000000000) >> 40
            c3 = (bits & 0x000000FF00000000) >> 32
            c4 = (bits & 0x00000000FF000000) >> 24
            c5 = (bits & 0x0000000000FF0000) >> 16
            c6 = (bits & 0x000000000000FF00) >> 8
            c7 = (bits & 0x00000000000000FF)
            return [(c0, c1, c2), (c3, c4, c5), (c6, c7, 0)]

        else:
            c0 = (bits & 0xFF000000) >> 24
            c1 = (bits & 0x00FF0000) >> 16
            c2 = (bits & 0x0000FF00) >> 8
            c3 = (bits & 0x000000FF)
            return [(c0, c1, c2), (c3, 0, 0)]

    def decode(self, colors):
        if colors == self.NullColor:
            return None
        if self.option['type'] == 'double':
            bits = colors[0][0] << 56
            bits |= colors[0][1] << 48
            bits |= colors[0][2] << 40

            bits |= colors[1][0] << 32
            bits |= colors[1][1] << 24
            bits |= colors[1][2] << 16

            bits |= colors[2][0] << 8
            bits |= colors[2][1]
        else:
            bits = colors[0][0] << 24
            bits |= colors[0][1] << 16
            bits |= colors[0][2] << 8

            bits |= colors[1][0]

        return self.toValue_IEEE754(bits)

    def toBits_IEEE754(self, value):
        if value == 0:
            return self.Zero

        bits = 0
        if value < 0:
            bits = 1
            value = -value
        vz = int(value)
        _vp = value - vz

        cnt_exponent = 0
        cnt_fraction = self.len_fraction
        fraction = 0
        if vz > 0:
            while (vz >> cnt_exponent) > 1:
                cnt_exponent += 1
            fraction = vz & ((1 << cnt_exponent) - 1)
            cnt_fraction -= cnt_exponent
        else:
            while _vp < 1 and cnt_exponent > -self.move_exponent:
                _vp = _vp * 2
                cnt_exponent -= 1
            _vp -= 1

        while cnt_fraction >= 0:
            cnt_fraction -= 1
            fraction <<= 1
            _vp = _vp * 2
            if _vp >= 1:
                _vp -= 1
                fraction |= 1

        bits = (bits << self.len_exponent) | (cnt_exponent + self.move_exponent)
        bits = (bits << self.len_fraction) | (((fraction + 1) >> 1) & self.mask_fraction)

        return bits

    def toValue_IEEE754(self, bits):
        if bits == self.Zero:
            return 0
        fraction = bits & self.mask_fraction
        cnt_exponent = ((bits & self.mask_exponent) >> self.len_fraction) - self.move_exponent
        cnt_fraction = self.len_fraction
        vz = 0
        if cnt_exponent >= 0:
            cnt_fraction -= cnt_exponent
            vz = (1 << cnt_exponent) | (fraction >> cnt_fraction)
        else:
            fraction = (1 << cnt_fraction) | fraction
            cnt_fraction -= cnt_exponent

        _vp = fraction & ((1 << cnt_fraction) - 1)
        _cnt = cnt_fraction
        while _cnt > 0:
            _cnt -= 1
            if _vp & (1 << _cnt) > 0:
                vz += 1 / (1 << (cnt_fraction - _cnt))

        if vz < 1e-20:
            return 0

        if bits & (1 << self.total_len) > 0:
            return -vz
        else:
            return vz



import math
import numpy as np
from PIL import Image

class ColorData:

    def __init__(self, img):
        self.img = img
        self.heigh = self.img.size[0]
        self.width = self.img.size[1]
        self.dc = DeColor({'type': 'double'})
        if self.img.mode == 'L':
            self.mode_len = 8
        elif self.img.mode == 'RGB':
            self.mode_len = 3

    def getxy(self, index, reserverow = 1):
        y = reserverow + math.floor(index * self.mode_len / self.width)
        x = index * self.mode_len - (y - reserverow) * self.width
        return x, y

    def setValue(self, index, value, reserverow = 1):
        x, y = self.getxy(index, reserverow)

        pixels = self.dc.encode(value)

        if self.img.mode == 'RGB':
            self.img.putpixel((x, y), pixels[0])
            self.img.putpixel((x + 1, y), pixels[1])
            self.img.putpixel((x + 2, y), pixels[2])
        elif self.img.mode == 'L':
            self.img.putpixel((x, y), pixels[0][0])
            self.img.putpixel((x + 1, y), pixels[0][1])
            self.img.putpixel((x + 2, y), pixels[0][2])
            self.img.putpixel((x + 3, y), pixels[1][0])
            self.img.putpixel((x + 4, y), pixels[1][1])
            self.img.putpixel((x + 5, y), pixels[1][2])
            self.img.putpixel((x + 6, y), pixels[2][1])
            self.img.putpixel((x + 7, y), pixels[2][0])

    def getValue(self, index, reserverow = 1):
        x, y = self.getxy(index, reserverow)
        
        if self.img.mode == 'RGB':
            p0 = self.img.getpixel((x, y))
            p1 = self.img.getpixel((x + 1, y))
            p2 = self.img.getpixel((x + 2, y))
            return self.dc.decode([p0, p1, p2])
        elif self.img.mode == 'L':
            p0 = self.img.getpixel((x, y))
            p1 = self.img.getpixel((x + 1, y))
            p2 = self.img.getpixel((x + 2, y))
            p3 = self.img.getpixel((x + 3, y))
            p4 = self.img.getpixel((x + 4, y))
            p5 = self.img.getpixel((x + 5, y))
            p6 = self.img.getpixel((x + 6, y))
            p7 = self.img.getpixel((x + 7, y))
            return self.dc.decode([(p0, p1, p2), (p3, p4, p5), (p6, p7, 0)])

    def setString(self, index, str, reserverow = 1):
        pixels = self.dc.encodeStr(
            width=self.width * self.mode_len,
            str=str
        )

        if self.img.mode == 'RGB':
            for i in range(len(pixels)):
                self.img.putpixel((i, index + reserverow), pixels[i])
        elif self.img.mode == 'L':
            for i in range(len(pixels)):
                self.img.putpixel((i*3, index + reserverow), pixels[i][0])
                self.img.putpixel((i*3+1, index + reserverow), pixels[i][1])
                self.img.putpixel((i*3+2, index + reserverow), pixels[i][2])


    def getString(self, index, reserverow = 1):
        colors = [];
        for x in range(self.width):
            colors.append(self.img.getpixel((x, index + reserverow)))

        if self.img.mode == 'RGB':
            return self.dc.decodeStr(colors);
        elif self.img.mode == 'L':
            cs = []
            for ci in range(0, len(colors), 3):
                cs.append((colors[ci], colors[ci+1], colors[ci+2]))
            last = len(colors) - len(cs)*3
            if last == 1:
                cs.append((colors[-2], colors[-1], 0))
            elif last == 2:
                cs.append((colors[-1], 0, 0))
            return self.dc.decodeStr(cs);


class Light:
    def enlight(self, data1, data2):
        return Image.fromarray(data1 ^ data2)

    def delight(self, data, data_delta):
        return Image.fromarray(data ^ data_delta)




if __name__ == '__main__':
    def _calsize(nodenum, mode):
        base = 3 * 8
        size = math.ceil(math.sqrt(nodenum * mode))
        return size + base - (size % base)

    MODE_RGB = 3 #3个像素存放一个值
    MODE_L   = 8 #8个像素存放一个值

    print('根据工况点个数，推荐图片尺寸')
    print('\t工况点个数\t|\tRGB size\t|\tL size')
    print('----------------|---------------|--------------')
    for n in range(600, 3000, 300):
        s_rgb = _calsize(n, MODE_RGB)
        s_l = _calsize(n, MODE_L)
        print('\t %d \t\t|\t %d * %d \t|\t %d * %d'%(n, s_rgb, s_rgb, s_l, s_l))
    print("\n")

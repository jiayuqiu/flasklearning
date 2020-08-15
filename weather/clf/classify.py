#! anaconda python
# -*- coding:utf-8 -*-
# 作者：邱家瑜
# 创建：2020-06-15
# 更新：2020-06-15
# 用意：根据海况分类参数信息，进行海况分级

from .utils.SeaState import WIND_LEVEL_SPEED, SEA_STATE_DICT


class SeaStateCLF(object):
    def __init__(self, wind_speed, wave_height, stream_speed=None, swell_height=None):
        self.wind_speed = wind_speed
        self.wave_height = wave_height
        self.stream_speed = stream_speed
        self.swell_height = swell_height
    
    def clf(self, method='static'):
        est = WeatherCLF(method).make()
        level = est.clf(self.wind_speed, self.wave_height)
        return level


# ----------------------------------------------------------------------------------------------
# classify method

class StaticCLF(object):
    @staticmethod
    def clf(wind_speed, wave_height):
        """对风与浪进行判断海况等级

        海况等级分类参数:
        0	浪高:0米,风力0级	
        1	浪高0-0.1米,风力1级	
        2	浪高0.1-0.5米,风力2级	
        3	浪高:0.5-1.25米,风力3-4级	
        4	浪高:1.25-2.50米,风力5级	
        5	浪高:2.50-4米,风力6级	
        6	浪高:4-6米,风力7级	
        7	浪高:6-9米,风力8-9级	
        8	浪高:9-14米,风力10-17级	
        9	浪高:14米以上,风力17级以上

        风力等级 - 风速(m/s)对应参数:
        0   0.0-0.2
        1   0.3-1.5
        2   1.6-3.3
        3   3.4-5.4
        4   5.5-7.9
        5   8.0-10.7
        6   10.8-13.8
        7   13.9-17.1
        8   17.2-20.7
        9   20.8-24.4
        10  24.5-28.4
        11  28.5-32.6
        12  32.7-36.9

        Returns:
            [int]: [海况等级 0 - 9 级]
        """
        # get wind level
        wind_level = -1
        for _, wlevel in enumerate(WIND_LEVEL_SPEED.keys()):
            if (wind_speed >= WIND_LEVEL_SPEED[wlevel]['min']) & (wind_speed <= WIND_LEVEL_SPEED[wlevel]['max']):
                wind_level = wlevel
            else:
                pass

        # get sea state level
        sea_state_level_list = list()
        if wind_level == -1:
            print('获取风力等级失败')
            raise('获取风力等级失败')
        else:
            for _, slevel in enumerate(SEA_STATE_DICT.keys()):
                # 判断风力与浪高
                bool_wind_level = (wind_level >= SEA_STATE_DICT[slevel]['wind_level']['min']) & (wind_level <= SEA_STATE_DICT[slevel]['wind_level']['max'])
                bool_wave_height = (wave_height >= SEA_STATE_DICT[slevel]['wave_height']['min']) & (wave_height <= SEA_STATE_DICT[slevel]['wave_height']['max'])
                if bool_wind_level | bool_wave_height:
                    sea_state_level_list.append(slevel)
                else:
                    pass
        
        # 获取最恶劣的海况等级
        sea_state_level = max(sea_state_level_list)
        return sea_state_level


class WeatherCLF(object):
    """气象分类，分类功能工厂
    """
    def __init__(self, method='static'):
        self.method = method
    
    def make(self, ):
        if self.method == 'static':
            return StaticCLF()
        else:
            raise(f'没有该分类方法: {self.method}')
    
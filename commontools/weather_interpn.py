#!/usr/bin/env python
# encoding: utf-8
import pandas as pd
import numpy as np
from weather import generate_weather_data, latProcess
from sqlalchemy import create_engine

def integrate():
    engine = create_engine("mysql+pymysql://root:Root@123@192.168.7.209:13306/feature_extend")
    data = pd.read_sql("select `prev_timestamp`,`ship_name`,`longitude_1`,`latitude_1` from tab_sailing_60",
                       con=engine)
    data['prev_timestamp'] = data['prev_timestamp'].astype(int)
    data['longitude_1'] = data['longitude_1'].astype('double')
    data['latitude_1'] = data['latitude_1'].astype('double')
    data.dropna(axis=0,how="any",subset=['longitude_1','latitude_1'], inplace=True)


    weather_columns = ['current_magnitude', 'current_direction', 'wind_magnitude', 'wind_direction', 'wave_height',
                       'wave_period', 'wave_direction', 'swell_height', 'swell_period', 'swell_direction',
                       'surface_pressure', 'surface_temperature', '500mB_height']
    columns = list(data.columns)
    columns.extend(weather_columns)

    res_df = pd.DataFrame(columns=columns)

    for i in range(data.shape[0]):
        if i%200 == 0:
            print(f'{i}/{data.shape[0]}')
        row = data.iloc[i]
        lng = row['longitude_1']
        lat = row['latitude_1']
        timestamp = row['prev_timestamp']

        res = generate_weather_data(lng, lat, timestamp)

        # # 转换经纬度
        # row['longitude_1'], row['latitude_1'] = latProcess(lng), latProcess(lat)

        if res is not None:
            row_list = list(row)
            row_list.extend(list(res))
            temp_df = pd.DataFrame(dict(zip(columns, row_list)), index=["0"])
            res_df = res_df.append(temp_df, ignore_index=True)
    res_df.to_sql("weather_interpn_data",con=engine,if_exists="append",index=True)

if __name__ == "__main__":
    integrate()

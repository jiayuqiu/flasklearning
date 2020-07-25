#!/usr/bin/env
# -*- coding:utf-8 -*-


"""
招商船舶数据质量评估并入库
"""

from tqdm import tqdm
import pandas as pd
from sqlalchemy import create_engine


def quality_statistics(key_table_info: dict,
                       pointvalue_table_info: dict,
                       statistics_table_info: dict) -> None:
    """
    统计招商工况记录数据质量，并入库.
    :param key_table_info: 工况字段表信息 （连接，表名）
    :param pointvalue_table_info: 工况记录表信息 （连接，表名）
    :param statistics_table_info: 数据质量记录表信息 （连接，表名）
    :return:
    """

    key_con = create_engine(key_table_info['conn'])
    key_table = pd.read_sql(f"select `KeyValue`, `desc_cn` from {key_table_info['table_name']}", con=key_con)
    key_table.drop_duplicates(inplace=True)

    pointvalue_con = create_engine(pointvalue_table_info['conn'])
    pointvalue_table_unique_keys = list(pd.read_sql(f"select distinct `key` from {pointvalue_table_info['table_name']}",
                                               con=pointvalue_con)['key'])

    key_list = []
    desc_list = []
    record_num_list = []
    null_num_list = []
    null_perc_list = []
    zero_num_list = []
    zero_perc_list = []
    negative_num_list = []
    negative_perc_list = []
    total_num_list = []
    total_perc_list = []

    res = {}

    for key, desc in tqdm(zip(key_table['KeyValue'], key_table['desc_cn'])):
        if key not in pointvalue_table_unique_keys:
            continue
        record_num = pd.read_sql(f"select count(*) from {pointvalue_table_info['table_name']} where `key`='{key}'",
                                 con=pointvalue_con)['count(*)'][0]

        null_num = pd.read_sql(f"select count(*) from {pointvalue_table_info['table_name']} where "
                               f"`key`='{key}' and (`value` is NULL or `value`='NULL')",
                               con=pointvalue_con)['count(*)'][0]
        null_perc = null_num / record_num

        zero_num = pd.read_sql(f"select count(*) from {pointvalue_table_info['table_name']} where `key`='{key}' and `value`='0'",
                               con=pointvalue_con)['count(*)'][0]
        zero_perc = zero_num / record_num

        negative_num = pd.read_sql(f"select count(*) from {pointvalue_table_info['table_name']} where `key`='{key}' and `value`<'0'",
                                   con=pointvalue_con)['count(*)'][0]

        negative_perc = negative_num / record_num

        total_num = null_num + zero_num + negative_num
        total_perc = total_num / record_num

        key_list.append(key)
        desc_list.append(desc)
        record_num_list.append(record_num)
        null_num_list.append(null_num)
        null_perc_list.append(null_perc)
        zero_num_list.append(zero_num)
        zero_perc_list.append(zero_perc)
        negative_num_list.append(negative_num)
        negative_perc_list.append(negative_perc)
        total_num_list.append(total_num)
        total_perc_list.append(total_perc)

    res['KeyValue'] = key_list
    res['desc_cn'] = desc_list
    res['null_num'] = null_num_list
    res['null_perc'] = null_perc_list
    res['zero_num'] = zero_num_list
    res['zero_perc'] = zero_perc_list
    res['negative_num'] = negative_num_list
    res['negative_perc'] = negative_perc_list
    res['total_num'] =  total_num_list
    res['total_perc'] = total_perc_list
    res['record_num'] = record_num_list

    res_df = pd.DataFrame(data=res)
    statistics_conn = create_engine(statistics_table_info['conn'])
    res_df.to_sql(statistics_table_info['table_name'], statistics_conn, if_exists='replace')

    print(f"计算完成，{statistics_table_info['table_name']}入库成功")


if __name__ == '__main__':
    # 数据库表信息
    KEY_TABLE_INFO = {'conn': 'mysql+pymysql://root:Root@123@192.168.7.209:13306/dc',
                      'table_name': 'tab_hldkeymap_83'}
    POINTVALUE_TABLE_INFO = {'conn': 'mysql+pymysql://root:Root@123@192.168.7.209:13306/dc',
                             'table_name': 'tab_pointvalue_83'}
    STATISTICS_TABLE_INFO = {'conn': 'mysql+pymysql://root:Root@123@192.168.7.209:13306/dc_data_quality',
                             'table_name': 'tab_statistics_83'}

    quality_statistics(key_table_info=KEY_TABLE_INFO,
                       pointvalue_table_info=POINTVALUE_TABLE_INFO,
                       statistics_table_info=STATISTICS_TABLE_INFO)
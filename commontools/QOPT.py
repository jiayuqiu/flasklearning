# coding:utf-8

import getopt


def get_param(argv):
    """
    描述参数信息

    应用: run.py
                         [-h|--help]

    Description:
        -h,--help        显示参数帮助信息
        -c,--config      配置文件路径

    Example:
        # 查询参数帮助
        python run.py --help

        # 生成测试数据
        python run.py --config=/Users/highlander/PycharmProjects/dataclean/conf/config.yaml 
    """
    config_path = ""

    try:
        opts, args = getopt.getopt(argv, "hc:", ["help", "config="])
    except getopt.GetoptError:
        print(get_param.__doc__)
        exit(1)

    for opt, arg in opts:
        if opt == '-h':
            print(get_param.__doc__)
            exit(1)
        elif opt in ("-c", "--config"):
            config_path = arg

    return config_path

import json
import re

import pandas as pd


def convert_data_file_2_list(path, read_method):
    df = read_method(path)
    df_list = []
    for i in df.index.values:
        # loc为按列名索引 iloc 为按位置索引，使用的是 [[行号], [列名]]
        df_line = df.loc[i].to_dict()
        # 将每一行转换成字典后添加到列表
        df_list.append(df_line)
    return df_list


def covert_excel_list(path):
    """
    pandas 读取 excel 内容转换为 List
    :param path:
    :return:
    """
    return convert_data_file_2_list(path, pd.read_excel)


def convert_csv_list(path):
    """
    pandas 读取 csv 内容转换为 list
    :param path:
    :return:
    """
    return convert_data_file_2_list(path, pd.read_csv)


def convert_list_2_dict(data, key_column):
    """
    List 转换成 dict
    :param data:
    :param key_column:
    :return:
    """
    result = {}
    for i in data:
        result[str(i[key_column])] = i
    return result


def convert_dict(path, key_column):
    """
    读取数据并转换为 dict
    :param path:
    :param key_column:
    :return:
    """
    data = {}
    if path.__contains__('.xls'):
        data = covert_excel_list(path)
    elif path.__contains__('.csv'):
        data = convert_csv_list(path)
    elif path.__contains__('.json'):
        data = read_from_json(path)
    return convert_list_2_dict(data, key_column)


def compare_raw(key, left_raw, right_raw, compare_column):
    # print("--------------------------------------")
    for t in compare_column:
        left_val = left_raw[t[0]]
        right_val = right_raw[t[1]]
        if left_val != right_val:
            print(f"key = {key}, {t[0]} = {left_val} 与 {t[1]} = {right_val}不匹配")
        else:
            print(f"数据一致, key = {key}, left = {left_val}, right = {right_val}")


def compare_data(left_dict, right_dict, relate_column, compare_column):
    print("以左边为准比较是否一致")
    for key, left_raw in left_dict.items():
        if key not in right_dict:
            print(f"右边数据 key = {key} 不存在")
            continue
        right_raw = right_dict[key]
        compare_raw(key, left_raw, right_raw, compare_column)

    print("以右边为准比较是否存在")
    for key, _ in right_dict.items():
        if key not in left_dict:
            print(f"左边数据 key = {key} 不存在")
    ...


def compare(left_path, right_path, relate_column, compare_column):
    # left_dict = convert_map(left_path, map(lambda x: x[0], relate_column))
    # right_dict = convert_map(right_path, map(lambda x: x[0], relate_column))
    left_dict = convert_dict(left_path, relate_column[0])
    right_dict = convert_dict(right_path, relate_column[1])

    compare_data(left_dict, right_dict, relate_column, compare_column)
    ...


def re_log(log):
    """
    替换空白字符 tab 换行符等，并通过正则匹配到真正的数据
    :param log:
    :return:
    """
    log_ = json.loads(re.findall('body:(.*?),tookMs', log.replace('\n', '').replace(' ', '').replace('\t', ''), 0)[0])
    return log_


def flatten(x):
    """
    展开 List[List] 为 List
    :param x:
    :return:
    """
    if isinstance(x, list):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]


def read_from_json(path):
    """
    从 kibana 拉取日志 json 数据
    :return:
    """
    if path.__contains__('.json') is False:
        return []
    with open(path) as f:
        load = json.load(f)
        # print(load)
        hits_ = load['hits']['hits']
        # print(hits_)
        logs = list(filter(lambda x: x['_source']['log'].__contains__('<--response start'), hits_))
        log_sources = list(map(lambda x: x['_source']['log'], logs))
        jsons = list(map(re_log, log_sources))
        data = flatten(list(map(lambda x: x['dataList'], jsons)))
        return data


if __name__ == '__main__':
    # compare('XingRen_Data.csv', 'yinte.xlsx', ('skuId', 'interface_code'), [('totalRemaining', 'stock')])
    # read_from_json()
    compare('XingRen_Data.csv', 'log.json', ('skuId', 'code'), [('totalRemaining', 'stock')])
    # compare('XingRen_Data.csv', 'XingRen_Data2.csv', ('skuId', 'skuId'), [('totalRemaining', 'totalRemaining')])


#!/usr/bin/env python3
#conding:utf-8
import os
import re
import time
import sys
import csv
import pandas as pd
import matplotlib.pyplot as plt


def get_csv_file_name():
    cwd = sys.path[0]
    filenames = os.listdir(cwd)
    csv_file_names = [x for x in filenames if x[-4:] == '.csv']
    print('csv files going to generate graphic: {0}\n'.format(csv_file_names))
    return csv_file_names


def group_data(csv_file_names):
    '''接收的csv表格结构为['DieNumber', 'ErrBit', 'FrameCnt', 'Rate'] '''
    df_empty = pd.DataFrame(columns=['TempSet', 'DieNumber', 'ErrBit', 'FrameCnt', 'Rate'])
    for csv_file in csv_file_names:
        temp_set = csv_file[:-4]    # 获取温度组合的名字
        df_temp = pd.read_csv(csv_file)
        
        # 以die为单位，重组数据


csv_file_name_list = get_csv_file_name()
#!/usr/bin/env python3
# Coding:UTF-8
import os
import re
import datetime
import os
import re
import time
import pickle
from collections import Counter

current_traces = [{'SN':'1178', 'info_str':'str', 'info_list':['list_item1','list_item2']}]
old_traces = [{'SN':'1178', 'info_str':'str_old', 'info_list':['list_item1','list_item2','list_item3']}]
normal_cards_sn = ['1178']

def timeStamp():
    now_time = datetime.datetime.now()
    readable_time = now_time.strftime('%Y-%m-%d_%H_%M_%S')
    return readable_time

def process_normal_mode(normal_cards_sn):
    '''
    即不存在新插入卡，也不存在移除卡的情况下，执行该函数，
    该函数比较相同sn的ssd在两次不同时间的扫描下，各项信息是否一致，并通知给主控服务器
    '''
    now_time = timeStamp()
    new_traces = []

    for sn in normal_cards_sn:
        change_info = ''
        
        current_trace = [trace for trace in current_traces if trace['SN'] == sn][0]
        old_trace = [trace for trace in old_traces if trace['SN'] == sn][0]

        for key in current_trace:
            if key in old_trace:
                if current_trace[key] != old_trace[key]:
                    info = '{0}: {1} ==> {2}\n'.format(key, old_trace[key], current_trace[key])
                else:
                    info = ''
            else:
                info = '{0}: ? ==> {1}\n'.format(key, current_trace[key])
            change_info = change_info + info
        new_trace = ['C', now_time, sn, change_info]
        new_traces.append(new_trace)
    print(new_traces)
    # send_to_server = send_info(new_traces)
    return
process_normal_mode(normal_cards_sn)
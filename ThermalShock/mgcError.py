# -*-coding: utf-8 -*-

import os
import time
import re
import csv

def get_mgcError():  # 获取mgc错误信息统计
    
    mgc_num = ['#419b','#519b','#b19b','#c19b']
    mgc_error_info = []
    get_mgc_cmd = './nvme dera get-log /dev/nvme0'
    
    for mgc in mgc_num:
        mgc_ready_cmd = "./nvme dera uart-in -p '{0} 0 0' /dev/nvme0".format(mgc)
        os.popen(mgc_ready_cmd)
        time.sleep(1)
        get_current_mgc_error_info = os.popen(get_mgc_cmd).readlines()  # 获取当前mgc的error info 信息
        mgc_error_info.extend(get_current_mgc_error_info)   # 存储到mgc_error_info变量中
    
    return mgc_error_info

def list_to_csv(list_name, filename):   # 将数据转换为csv格式的文件
    # 检查列表是否为空
    if not list_name:
        print('list is empty.')
        return
    # 调用re.split()对list逐个字符元素进行分割，非字符元素将被丢弃
    selected_list = []
    # print(list_name) # kou debug...
    for list_line in list_name:
        if isinstance(list_line, str):
            list_line.strip('\n')
            if 'ERRBit' in list_line:
                splited = re.split(r'[.=,]', list_line) # 将长字符以 . , = 为分界，分解为列表
                if len(splited) < 10:
                    selected = [list_line]  
                else:
                    selected = [splited[5], splited[7], splited[9]]
                # print(splited)
            elif 'ERRUNC' in list_line:
                splited = re.split(r'[.=,>]', list_line)
                if len(splited) < 10:
                    selected = [list_line] 
                else:
                    selected = ['>72', splited[7], splited[9]]
                # print(splited)
            elif 'TotalReadECCFrameCnt' in list_line:
                splited = re.split(r'[,=]', list_line)
                if len(splited) < 7:
                    selected = [list_line]
                else:
                    selected = ['Total',splited[2], splited[4]]
                # selected = ['Total',splited[2], splited[4]]
                # print(splited)
                # print(selected)
            elif 'cpu_mask' in list_line:
                splited = re.split(r'[ ]', list_line)
                if len(splited) < 10:
                    selected = [list_line]
                else:
                    selected = ['cpu_mask', splited[9]]
            elif not list_line:
                continue
            print(selected)    
            selected_list.append(selected)
    with open(filename,'a',newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['ErrBit','FrameCnt','Rate'])
        data = selected_list
        writer.writerows(data)
        csv_file.close()
    return

list_name = get_mgcError()
list_to_csv(list_name,'50-50.csv')

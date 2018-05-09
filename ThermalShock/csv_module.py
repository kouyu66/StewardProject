#!/usr/bin/env python3
# -*- Coding: UTF-8 -*-
import os
import csv
import time
import datetime
import re
from random import choice

def get_mgcError_by_die():  # 逐个die获取mgc错误统计信息 
    
    mgc_num_range = ['#419d', '#519d', '#b19d', '#c19d']
    rg_num_range = ['0','1']
    die_num_range = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    get_die_err_cmd = './nvme dera get-log /dev/nvme0'
    total_info = []

    for mgc in mgc_num_range:
        for rg in rg_num_range:
            for die in die_num_range:
                
                die_ready_cmd = "./nvme dera uart-in -p '{0} 1 {1} {2}' /dev/nvme0".format(mgc,rg,die)
                os.popen(die_ready_cmd)
                time.sleep(0.05) # wait for card info ready.
                get_current_die_err_info = os.popen(get_die_err_cmd).readlines()
                # [NMPa1 000d 02:30:12.445] ...RG=1,Die=12,ERRBit=070,FrameCnt=00000000000000000000,Rate=00000000
                line_info = []
                die_info = '{0},{1},{2}'.format(str(mgc_num_range.index(mgc)), rg, die)
                line_info.append(die_info)

                for line in get_current_die_err_info:
                    
                    split_line = [x for x in re.split(r'[.=,>]', line) if x]    # 目标行应包含12个元素
                    if len(split_line) == 12 and split_line[6] == 'ERRBit' and split_line[8] == 'FrameCnt' and split_line[10] == 'Rate':
                        Errbit = split_line[7]
                        FrameCnt = str(int(split_line[9]))  # 去掉framcnt计数多余显示的0
                        Rate = str(int(split_line[11]))     # 去掉rate计数多余显示的0
                        
                        bit_info = '{0}_{1}_{2}'.format(Errbit, FrameCnt, Rate)    
                        line_info.append(bit_info)
                    elif len(split_line) == 12 and split_line[6] == 'ERRUNC' and split_line[8] == 'FrameCnt' and split_line[10] == 'Rate':
                        Errbit = '>72'
                        FrameCnt = str(int(split_line[9]))  # 去掉framcnt计数多余显示的0
                        Rate = str(int(split_line[11]))     # 去掉rate计数多余显示的0
                        
                        bit_info = '{0}_{1}_{2}'.format(Errbit, FrameCnt, Rate)    
                        line_info.append(bit_info)
                    else:
                        pass
                total_info.append(line_info)
    return total_info

def list_to_csv_by_die(list_name, file_name):
    with open(file_name,'a',newline='') as csv_file:
        writer = csv.writer(csv_file)

        data = list_name
        writer.writerows(list_name)
        csv_file.close()
    return

list_name = get_mgcError_by_die()
list_to_csv_by_die(list_name, 'test_for_format.csv')
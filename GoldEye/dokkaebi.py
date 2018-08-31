#!/usr/bin/env python3
# -*- coding:utf-8 -*
# Author: kouxinyu
# Email: kouyu66@163.com
# Version: 0.0.1
# 后台监控进程，监控测试机的动作及ssd卡的状态
# linux only for now 模块化各个函数，以便于后续调用

import os
import re

# deraSSDMonitor()            # 用于监控dera ssd state信息的变动情况
# osInfoGenerator()           # 用于生成操作系统的关键信息
# powerOprationMonitor()      # 用于记录测试机的上下电相关动作
# messageGenerator()          # 关键信息生成器
# messageProcessor()          # 关键信息处理器
# ---------------------
def nvme_tool_check():
    '''检查nvme工具是否存在，并打印版本号'''
    if not os.path.exists('nvme'):
        print('- nvme tool not found. copy tools to current folder...')
        return_code = os.system('cp /system_repo/tools/nvme/nvme .')
        if return_code == 0:
            print('- nvme tool get successfully.')
        else:
            print('* warning: nvme tool get failed, please check network to drive T')
            exit()
    p_nvme_ver = (os.popen('./nvme version').read()).strip()
    print('- ' + p_nvme_ver)
    return 0

def ssd_state(node):
    '''输入字符设备，输出nvme状态信息（字典）'''

    state_info = {}
    list_temp = []
    get_state_cmd = './nvme dera state /dev/{0}'.format(node)       
    sep = ':'
    raw_out_put = os.popen(get_state_cmd).readlines()
    for line in raw_out_put:
        if line.count(sep) != 1:
            continue                                                # 抛弃分隔符不存在或不唯一的行
        seprate_line = re.split(sep, line)
        seprate_line = [
            x.replace('\t', '').replace('\n', '').replace(' ', '')  # 字符清理
            for x in seprate_line
        ]
        list_temp.append(seprate_line)
    state_info = dict(list_temp)
    return state_info

def state_comp(last_dict, current_dict):
    delete = []
    add = []
    update = []
    if last_dict == current_dict:
        return 0
    for key in last_dict.keys():
        # if last_dict[key] == 
        pass



last_dict = {'name':'jack'}
current_dict = {'name':'jack'}
print(last_dict.items())

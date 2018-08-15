#!/usr/bin/env python3
# -*- coding:utf-8 -*
# Author: kouxinyu
# Email: kouyu66@163.com
# Version: 0.0.1
# 后台监控进程，监控测试机的动作及ssd卡的状态
# linux only for now 模块化各个函数，以便于后续调用

import os

deraSSDMonitor()            # 用于监控dera ssd state信息的变动情况
osInfoGenerator()           # 用于生成操作系统的关键信息
powerOprationMonitor()      # 用于记录测试机的上下电相关动作
messageGenerator()          # 关键信息生成器
messageProcessor()          # 关键信息处理器
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

def ssd_state():
    pass

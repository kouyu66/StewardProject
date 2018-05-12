#!/usr/bin/env python3
# Coding:UTF-8
import os
import re

def process_normal_mode(normal_cards_sn):
    
    def process_script_change(info,key_info):
        
        global now_time
        last_list, current_list = info

        if not last_list:   # 检测到脚本启动
            if current_list[-1] == '1':  # 父进程为init进程，则当前进程由系统开机启动
                key_info['stop_time'] = ['',''] # 清空stop_time时间戳，因为检测到进程又自动启动了
            else:
                key_info['start_time'] = ['', now_time]    # 该进程非开机启动，发送启动时间戳
        elif not current_list:    # 检测到脚本终止
            key_info['stop_time'] = ['', now_time]  # 将stop_time时间戳写入        
        else:   # 检测到脚本信息变动：
            if last_list[:2] == current_list[:2]:
                if current_list[-1] == '1': # 检测到掉电脚本执行后的首次重启
                    del key_info['script']  # 忽略本次变更
            else:   # 检测到非开机启动进程，发送启动时间戳
                key_info['start_time'] = ['', now_time]
        return key_info



    for sn in normal_cards_sn:
        current_trace = [trace for trace in current_traces if trace['SN'] == sn][0]
        old_trace = [trace for trace in old_traces if trace['SN'] == sn][0]
        head_info = {'now_time': now_time,'SN': sn}
        key_info = {}

        for key in current_trace:
            if key in old_trace and current_trace[key] != old_trace[key]:
                key_info[key] = [old_trace[key], current_trace[key]]
                else:
                    continue

        # 增加对脚本启动时间的判断
        if key_info.get('script'):
            info = key_info.get('script')
            process_script_change(info)
        
        
        if not key_info:
            head_info['info_type': 'heartbeat']
        

        else:
            head_info['info_type': 'normal_update']
            head_info.update(key_info)
        



        json_info = json.dumps(key_info)
        send_info(json_info)
        # pass    # send heartbeat.
    return
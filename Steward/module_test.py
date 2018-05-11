#!/usr/bin/env python3
# Coding:UTF-8
import os
import re

def process_normal_mode(normal_cards_sn):
    
    def process_script_change(info):
        last_list, current_list = info
        if not last_list:
            if current_list[-1] == '1':  # 父进程为init进程，则当前进程由系统开机启动
                pass
            else:
                pass    # 该进程非开机启动
        if not current_list:
            

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
        if not key_info:
            head_info['info_type': 'heartbeat']
        else:
            head_info['info_type': 'normal_update']
            head_info.update(key_info)
        
        # 增加对脚本启动时间的判断
        if head_info.get('script'):
            info = head_info.get('script')
            process_script_change(info)



        json_info = json.dumps(key_info)
        send_info(json_info)
        # pass    # send heartbeat.
    return
#!/usr/bin/env python3
# chkconfig:2345 80 90
# description:crowbar.py
# coding:utf-8

import os
import re
import time
import datetime
import json
import socket
from collections import Counter

global node_info
global net_status
global uptime  # 友好可读的开机时间显示
global uptime_seconds  # 浮点数形式的开机时间，可用于计算
global now_time


# ------ 通用函数 ------ #
def get_pci_speed(disk_name):
    '''获取pci设备的速度，输入字符串nvme*, 输出字符串 *GT/s x*'''

    get_pci_bus_number_line_cmd = 'find /sys/* -name {0}|grep devices'.format(
        disk_name)
    pci_bus_number_line = os.popen(get_pci_bus_number_line_cmd).readlines()
    if pci_bus_number_line:
        pci_bus_number_line_str = pci_bus_number_line[0]
        split_bus_num = re.split('/', pci_bus_number_line_str)
        pci_bus_number = split_bus_num[-3]
    else:
        return 'Unknown'

    lspci_cmd = "lspci -vvv -s {0} | grep 'LnkSta:' | cut -d ' ' -f 2,4".format(
        pci_bus_number)
    lspci_info = os.popen(lspci_cmd).readlines()
    lspci_info_strip = [x.strip('\n') for x in lspci_info][0]

    pci_speed = ''.join(lspci_info_strip.split(','))

    return pci_speed

def load_ssd_info(node):
    '''获取ssd全部信息 输入字符串/dev/nvme*, 输出字典ssd_info'''

    disk_name = re.split('/', node)[-1]  # 获取nvme*
    ssd_info = {}
    # ------ 给ssd各项值赋值 ------ #
    # 获取dera info信息添加到字典
    get_dera_info_cmd = "./nvme dera info {0}".format(node)
    dera_info = os.popen(get_dera_info_cmd).readlines()
    info_dict = list_to_dict(dera_info)
    if not info_dict:
        return
    ssd_info.update(info_dict)

    # 获取status信息并添加到字典
    get_dera_state_cmd = "./nvme dera state {0}".format(node)
    dera_state = os.popen(get_dera_state_cmd).readlines()
    state_dict = list_to_dict(dera_state)
    if not state_dict:
        return
    ssd_info.update(state_dict)
    
    # 获取pci速度信息添加到字典
    pci_speed_processed = get_pci_speed(disk_name)
    ssd_info['pcispeed'] = pci_speed_processed

    # 获取boot 信息添加到字典
    get_boot_drive_cmd = "df -h | grep -E '/boot$'"
    boot_drive_info = os.popen(get_boot_drive_cmd).readlines()[0]
    if disk_name in boot_drive_info:
        boot = 'Master'
    else:
        boot = 'Slave'
    ssd_info['boot'] = boot

    return ssd_info

def list_to_dict(list_info, sep=':'):
    '''将包含冒号的长字符串转换为字典格式，输入列表，输出字典'''

    list_temp = []

    for line in list_info:
        if line.count(sep) != 1:    # 检查分隔符数量是否为1
            continue
        seprate_line = re.split(sep, line)
        seprate_line = [
            x.replace('\t', '').replace('\n', '').replace(' ', '')
            for x in seprate_line
        ]
        list_temp.append(seprate_line)
    dict_info = dict(list_temp)

    return dict_info

def timeStamp():
    client_time = datetime.datetime.now()
    # 标注为测试机本地的时间戳
    readable_time = client_time.strftime('%Y-%m-%d %H:%M:%S') + '[Machine]'
    return readable_time

def get_uptime():
    '''获取linux开机时长信息，返回两个值，第一个为浮点数开机秒，第二个为可读字符串'''

    # 获取服务器开机时长信息
    get_uptime_command = "cat /proc/uptime | cut -d ' ' -f 1"
    uptime_seconds_str = os.popen(get_uptime_command).readlines()[0]
    uptime_seconds = float(uptime_seconds_str)

    m, s = divmod(uptime_seconds, 60)
    h, m = divmod(m, 60)
    uptime = "%02d:%02d:%02d" % (h, m, s)

    return uptime_seconds, uptime

def get_node_info():
    '''获取dera nvme ssd字符设备信息'''
    global node_info

    get_nvme_node_command = "ls /dev/nvme* | grep nvme.$"
    node_info_raw = os.popen(get_nvme_node_command).readlines()
    node_info = [
        x.replace('\n', '').replace(' ', '').replace('\t', '')
        for x in node_info_raw if node_info_raw
    ]
    for node in node_info:
        identify_info = os.popen(
            "./nvme id-ctrl {0} | grep ^vid".format(node)).readlines()
        if identify_info and '0x1d78' not in identify_info[0]:  # 排除非dera ssd
            node_info.remove(node)
    return node_info

def get_net_status():
    '''获取网络状态信息'''
    global net_status

    local = '10.0.4.1'  # 本地网关
    t_disk = '10.0.1.206'  # T盘所在服务器的IP地址
    overmind = '10.0.4.155' # 主控所在服务器ip  
    net_bucket = [local, t_disk, overmind]
    net_status = ['1', '1', '1']

    for ip in net_bucket:
        ping_command = 'ping {0} -c 2 -w 2'.format(ip)
        respond = os.popen(ping_command).readlines()
        for line in respond:
            if 'ttl' in line:
                index = net_bucket.index(ip)
                net_status[index] = '0'
            else:
                continue
    net_status = ''.join(net_status)
    return net_status


# ------ 获取信息 ------ #
def get_data():
    '''通过内置函数生成当前测试信息条目，上次测试信息条目'''

    def get_running_script():
        '''获取当前正在运行的脚本及参数，pid. 返回列表[[command1, args, ppid]]'''

        get_script_cmd = "ps -elf | grep -E 'HotPlug_NVMe_suite\.py|ts_.*\.py |runvdb\.py |thermal_shock\.py'|grep -v grep"
        raw_script_list = os.popen(get_script_cmd).readlines()
        commands = []

        for line in raw_script_list:
            raw_split_line = re.split(' ', line)
            split_line = [x.strip('\n') for x in raw_split_line if x]

            for item in split_line:
                if '.py' in item:
                    script_name = item
                    script_args = ' '.join(split_line[split_line.index(item) + 1:])
                    ppid = split_line[4]
                    command = [script_name, script_args, ppid]
                    commands.append(command)

        return commands

    def get_machine_status():
        '''获取当前测试机信息，[厂商, 型号, cpu, 内存, nvme node, 开机时间, 网络状态]'''

        global uptime  # 友好可读的开机时间显示
        global uptime_seconds  # 浮点数形式的开机时间（秒）

        # 定义相关命令
        get_manufacturer_command = 'dmidecode -s system-manufacturer && dmidecode -s system-product-name'
        get_cpu_type_command = 'dmidecode -s processor-version'
        get_mem_count_command = 'dmidecode -t memory | grep Size: | grep -v No'
        get_mem_type_command = "dmidecode -t memory | grep -E 'Type: DDR|Type: DRAM'|uniq"
        

        # 获取服务器厂商，型号信息
        machine_info = os.popen(get_manufacturer_command).readlines()
        machine_info = [x.strip('\n').strip() for x in machine_info]
        manufacturer, machine_type = machine_info

        # 获取服务器CPU信息
        cpu_info = os.popen(get_cpu_type_command).readlines()
        cpu_info = [x.strip('\n').strip() for x in cpu_info]
        cpus = ' '.join([
            '{0}*{1}'.format(str(x), str(y))
            for x, y in Counter(cpu_info).items()
        ])

        # 获取服务器内存信息
        mem_count = os.popen(get_mem_count_command).readlines()
        mem_count = [x.strip('\n').strip().replace('Size','Mem') for x in mem_count]
        mem_type = os.popen(get_mem_type_command).readlines()
        mem_type = [x.strip('\n').strip().replace('Type: ', '') for x in mem_type][0]
        mem_dict = Counter(mem_count)
        mems = ' '.join(['{0}*{1} {2}'.format(str(x), str(y), mem_type) for x, y in mem_dict.items()])

        host_info = '{0}_{1}_{2}_{3}'.format(manufacturer, machine_type, cpus,
                                             mems)

        return host_info

    def genarate_current_trace():  # 生成trace列表

        global node_info

        traces = []
        running_script = []
        machine = get_machine_status()
        scripts = get_running_script()

        for node in node_info:
            # 获取当前设备的脚本信息
            running_script = []
            for script in scripts:  

                if 'ts_pwr' in script[0] or 'ts_top' in script[0]:
                    running_script = script
                    break
                elif node in script[1]:  # 除掉电脚本外，特殊指明设备的脚本
                    running_script = script
                    break
            if not running_script:
                running_script = []

            ssd_info = load_ssd_info(node)  # 获取当前设备的状态信息
            if not ssd_info:
                continue    
            
            trace = dict([['machine', machine], ['script', running_script]])  
            trace.update(ssd_info)  # 生成trace

            # 删除不需要监控的trace消息:
            if 'host_write_commands' in trace:
                del trace['host_write_commands']
            if 'host_read_commands' in trace:
                del trace['host_read_commands']
            if 'data_units_written' in trace:
                del trace['data_units_written']
            if 'data_units_read' in trace:
                del trace['data_units_read']
            if 'current_power' in trace:
                del trace['current_power']
            if 'current_pcie_volt' in trace:
                del trace['current_pcie_volt']
            if 'cap_voltage' in trace:
                del trace['cap_voltage']
            if 'controller_busy_time' in trace:
                del trace['controller_busy_time']
            traces.append(trace)

        return traces

    def read_old_trace(file_name='last_trace.json'):
        if os.path.exists(file_name):
            with open(file_name) as last_trace_obj:
                old_traces = json.load(last_trace_obj)
        else:
            old_traces = []
        return old_traces

    current_traces = genarate_current_trace()
    old_traces = read_old_trace()

    return current_traces, old_traces


# ------ 处理信息 ------ #
def process_data(current_traces, old_traces):
    global now_time

    def send_info(data, server_ip='10.0.4.155'):
        global net_status
        net_info = list(net_status)
        if net_info[-1] != '0':  # 如果网络状态异常，则终止发送信息
            return
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((server_ip, 6001))
            s.send((data).encode('utf-8'))  # 发送客户端有效数据
            # print(s.recv(1024).decode('utf-8')) # 接受服务器端的返回信息
            s.send(('').encode('utf-8'))  # 发送终止信息（空字符）
            s.close()  # 关闭连接
        except ConnectionRefusedError as e:
            print('overmind not found...')
            return

    def list_compare(current_list, last_list):
        '''以第二个列表为基准，判断相对于第一个列表来说增加和减少的条目'''

        item_add = []
        item_remove = []
        for current_item in current_list:
            if current_item not in last_list:
                item_add.append(current_item)
            else:
                last_list.remove(current_item)
        if last_list:
            item_remove = last_list
        
        return item_add, item_remove

    def new_check(new_trace):
        '''对首次识别到的trace，筛选关键信息供生成dataframe用'''

        key_info = {
            'info_type': 'new_trace',
            'machine': new_trace.get('machine'),
            'script': new_trace.get('script'),
            'SN': new_trace.get('SN'),
            'Model': new_trace.get('Model'),
            'Capacity': new_trace.get('Capacity'),
            'FwRev': new_trace.get('FwRev'),
            'fw_loader_version': new_trace.get('fw_loader_version'),
            'uefi_driver_version': new_trace.get('uefi_driver_version'),
            'device_status': new_trace.get('device_status'),  # Normal
            'Format': new_trace.get('Format'),
            'pcispeed': new_trace.get('pcispeed'),  # 8GT/s x4
            'boot': new_trace.get('boot')
        }
        return key_info

    def process_card_add(add_cards_sn):
        '''
        生成特定识别信息，转交发送函数，发送给服务器
        '''
        for sn in add_cards_sn:
            for trace in current_traces:
                if trace['SN'] == sn:
                    # 筛选关键信息进行发送
                    key_infomation = new_check(trace)
                    json_info = json.dumps(key_infomation)
                    send_info(json_info)  # 发送给服务器
                    break
                else:
                    continue
        # json_info = json.dumps(new_traces)
        # send_info(json_info)  # 发送给服务器

        return

    def process_card_remove(remove_cards_sn):
        '''
        构建一条新的消息，报告给中央服务器，该卡已经在机器上被移除了
        '''
        global now_time

        for sn in remove_cards_sn:
            for old_trace in old_traces:
                if old_trace['SN'] == sn:
                    if old_trace['script'] == '':
                        err = 0
                    else:
                        err = 1
                    key_info = {
                        'info_type': 'card_remove',
                        'now_time': now_time,
                        'SN': sn,
                        'err': err
                    }
                    json_info = json.dumps(key_info)
                    send_info(json_info)
                    break
                else:
                    continue
        return

    def process_normal_mode(normal_cards_sn):
        def process_temp_change(key_info):
            '''只监控温度警告时的温度信息，如果变动信息不含警告信息，则忽略'''

            key_list = list(key_info.keys())

            for key in key_list:
                if 'temperature' in key:
                    del key_info[key]
            
            return key_info

        def process_script_change(info, key_info):
            '''根据脚本父进程判断脚本实际启动时间及终止时间'''

            global now_time
            last_list, current_list = info
            
            if current_list:
                if current_list[-1] == '1':
                    key_info['stop_time'] = ['', '']    # 检测到假启动，
                else:
                    key_info['start_time'] = ['', now_time]
            else:
                key_info['stop_time'] = ['', now_time]


            return key_info

        for sn in normal_cards_sn:
            current_trace = [
                trace for trace in current_traces if trace['SN'] == sn
            ][0]
            old_trace = [trace for trace in old_traces if trace['SN'] == sn][0]
            head_info = {'now_time': now_time, 'SN': sn}
            key_info = {}

            for key in current_trace:
                if key in old_trace and current_trace[key] != old_trace[key]:
                    key_info[key] = [old_trace[key], current_trace[key]]
                else:
                    continue

            # 增加对脚本启动时间的判断
            script_change = key_info.get('script')
            if script_change:
                key_info = process_script_change(script_change, key_info)

            # 2018_05_15 增加对温度打印的处理
            temp_warn = key_info.get('warning_temperature_time')
            temp_critical = key_info.get('critical_composite_temperature_time')
            if not temp_warn and not temp_critical:
                key_info = process_temp_change(key_info)
            # ------ 信息处理完成 ------ #

            if not key_info:
                head_info['info_type'] = 'heartbeat'

            else:
                head_info['info_type'] = 'normal_update'
                head_info.update(key_info)

            json_info = json.dumps(head_info)
            send_info(json_info)

        return

    def identify_card_status(current_traces, old_traces):
        '''根据上次扫描，判断卡当前状态'''

        current_cards_sn = [
            trace['SN'] for trace in current_traces if current_traces
        ]  # 获取当前trace中ssd的names部分
        last_cards_sn = [trace['SN'] for trace in old_traces
                         if old_traces]  # 获取上次扫描中ssd的names部分
        add_cards_sn = []
        remove_cards_sn = []
        normal_cards_sn = []

        add_cards_sn, remove_cards_sn = list_compare(
            current_cards_sn, last_cards_sn)  # 判断是否有丢卡，或新识别卡的情况发生
        normal_cards_sn = [
            x for x in current_cards_sn if x not in add_cards_sn
        ]  # 既不是新添加的卡，也不包含弹出的卡

        if add_cards_sn:
            process_card_add(add_cards_sn)
        if remove_cards_sn:
            process_card_remove(remove_cards_sn)
        if normal_cards_sn:
            process_normal_mode(normal_cards_sn)
        
        return

    identify_card_status(current_traces, old_traces)

    return


# ------ main logic ------ #
# 开机30秒以内为准备阶段，不做检查，等待脚本启动
# uptime_seconds, uptime = get_uptime()  # 脚本运行时首先判断开机时长

# while uptime_seconds < 30:
#     time.sleep(1)
#     uptime_seconds, uptime = get_uptime()

# 准备阶段结束，开始循环检查...

while True:
    global now_time
    global node_info
    global net_status
    now_time = timeStamp()
    node_info = get_node_info()
    net_status = get_net_status()

    current_traces, old_traces = get_data()
    process_data(current_traces, old_traces)

    with open('last_trace.json', 'w') as last_trace_obj:
        json.dump(current_traces, last_trace_obj)

    time.sleep(2)

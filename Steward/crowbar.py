#!/usr/bin/env python3
#chkconfig:2345 80 90
#description:crowbar.py
#coding:utf-8

import os
import re
import time
import datetime
import json
import socket
import sys
from collections import Counter
'''
ssd测试过程中用到的类信息
'''

global node_info
global net_status
global uptime  # 友好可读的开机时间显示
global uptime_seconds  # 浮点数形式的开机时间，可用于计算
global now_time


# ------ 通用函数 ------ #
class SSD():
    '''一次模拟SSD的尝试'''

    def __init__(self, node):
        self.node = node
        self.diskname = re.split('/', self.node)[-1]
        self.info = {}
        # self.pcispeed = ''
        # self.boot = ''
        # self.names = {} # [sn, mn, cap, boot, namespace]
        # self.status = {}    # [status, pcispeed, temps, cap_status, dev_status_up, current_pwr, ddr_err_bit, gpio_err_bit, pcie_voltage]
        # self.vers = {}  # [fw, fwld, fmt, uefi_driver]
        # self.counters = {}  # [powerCycles, powerOnHours, unsafe_shutdowns, full_rebulid, raw_rebuild]
        # self.err = {} # [pcie_uncorr_err, pcie_fatal_err, nand_init_fail, nand_erase_err, nand_program_err, media_err,init_pcie_vot_low_cnt, rt_pcie_vot_low_cnt]
    def load(self):
        '''更新ssd状态信息'''
        # 获取pci速度信息
        pci_speed_processed = get_pci_speed(self.disk_name)
        self.info['pcispeed'] = pci_speed_processed

        # 获取boot 信息
        get_boot_drive_cmd = "df -h | grep -E '/boot$'"
        boot_drive_info = os.popen(get_boot_drive_cmd).readlines()[0]
        if self.diskname in boot_drive_info:
            boot = 'Master'
        else:
            boot = 'Slave'
        self.info['boot'] = boot

        # 获取dera info信息并添加到字典
        get_dera_info_cmd = "./nvme dera info {0}".format(self.node)
        dera_info = os.popen(get_dera_info_cmd).readlines()
        self.info.update(list_to_dict(dera_info))

        # 获取status信息并添加到字典
        get_dera_state_cmd = "./nvme dera state {0}".format(self.node)
        dera_state = os.popen(get_dera_state_cmd).readlines()
        self.info.update(list_to_dict(dera_state))
        return

def list_to_dict(list_info, sep=':'):  # 输入列表， 以分隔符分隔， 输出字典
    '''将包含冒号的长字符串转换为字典格式'''
    list_temp = []

    for line in list_info:
        if line.count(sep) != 1:
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
    readable_time = client_time.strftime('%Y-%m-%d_%H_%M_%S')
    return readable_time

def get_uptime()
    # 获取服务器开机时长信息
    uptime_seconds_str = os.popen(get_uptime_command).readlines()[0]
    uptime_seconds = float(uptime_seconds_str)
    m, s = divmod(uptime_seconds, 60)
    h, m = divmod(m, 60)
    uptime = "%02d:%02d:%02d" % (h, m, s)

    return uptime_seconds, uptime

# ------ 获取信息 ------ #
def get_data():

    def get_pci_speed(disk_name):  # 查询ssd字符设备的的pcie速度
        get_pci_bus_number_line_cmd = 'find /sys/* -name {0}|grep devices'.format(
            disk_name)
        pci_bus_number_line = os.popen(get_pci_bus_number_line_cmd).readlines()[0]
        split_bus_num = re.split('/', pci_bus_number_line)
        pci_bus_number = split_bus_num[-3]

        lspci_cmd = "lspci -vvv -s {0} | grep 'LnkSta:' | cut -d ' ' -f 2,4".format(
            pci_bus_number)
        lspci_info = os.popen(lspci_cmd).readlines()
        lspci_info_strip = [x.strip('\n') for x in lspci_info][0]

        pci_speed = ''.join(lspci_info_strip.split(','))

        return pci_speed

    def get_running_script():  # 获取当前正在运行的脚本及参数，pid. 返回列表[[command1, args, ppid]]

        get_script_full_cmd = "ps -elf | grep -E 'HotPlug_NVMe_suite\.py|ts_.*\.py |runvdb\.py |thermal_shock\.py'|grep -v grep"
        raw_script_list = os.popen(get_script_full_cmd).readlines()
        commands = []

        for line in raw_script_list:
            raw_split_line = re.split(' ', line)
            split_line = [x.strip('\n') for x in raw_split_line if x]  # 去掉空字符及换行符

            for item in split_line:
                if '.py' in item:
                    script_name = item
                    script_args = ' '.join(split_line[split_line.index(item) + 1:])
                    ppid = split_line[4]
                    command = [script_name, script_args, ppid]
                    commands.append(command)
        return commands

    def get_machine_status():  # 获取当前测试机信息，[厂商, 型号, cpu, 内存, nvme node, 开机时间, 网络状态]
        '''获取当前测试机信息，[厂商, 型号, cpu, 内存, nvme node, 开机时间, 网络状态]'''
        global node_info  # 这两个变量用于判断，不需要发送到主控端，所以单列出来
        global net_status  # 这两个变量用于判断，不需要发送到主控端，所以单列出来
        global uptime  # 友好可读的开机时间显示
        global uptime_seconds  # 浮点数形式的开机时间，可用于计算

        # 定义相关命令
        get_manufacturer_command = 'dmidecode -s system-manufacturer && dmidecode -s system-product-name'
        get_cpu_type_command = 'dmidecode -s processor-version'
        get_mem_count_command = 'dmidecode -t memory | grep Size: | grep -v No'
        get_mem_type_command = "dmidecode -t memory | grep -E 'Type: DDR|Type: DRAM'|uniq"
        get_uptime_command = "cat /proc/uptime | cut -d ' ' -f 1"
        get_nvme_node_command = "ls /dev/nvme* | grep nvme.$"

        # 获取服务器厂商，型号信息
        machine_info = os.popen(get_manufacturer_command).readlines()
        machine_info = [x.strip('\n').strip() for x in machine_info]

        manufacturer, machine_type = machine_info

        # 获取服务器CPU信息
        cpu_info = os.popen(get_cpu_type_command).readlines()
        cpu_info = [x.strip('\n').strip() for x in cpu_info]
        cpus = ' '.join([
            '{0} * {1}'.format(str(x), str(y))
            for x, y in Counter(cpu_info).items()
        ])

        # 获取服务器内存信息
        mem_count = os.popen(get_mem_count_command).readlines()
        mem_count = [x.strip('\n').strip() for x in mem_count]
        mem_type = os.popen(get_mem_type_command).readlines()
        mem_type = [x.strip('\n').strip() for x in mem_type][0]
        mem_dict = Counter(mem_count)
        mems = ' '.join([
            '{0} * {1} {2}'.format(str(x), str(y), mem_type)
            for x, y in mem_dict.items()
        ])

        # 获取dera nvme ssd字符设备信息
        node_info = os.popen(get_nvme_node_command).readlines()
        node_info = [
            x.replace('\n', '').replace(' ', '').replace('\t', '')
            for x in node_info if node_info
        ]
        for node in node_info:
            identify_info = os.popen(
                "./nvme id-ctrl {0} | grep ^vid".format(node)).readlines()
            if identify_info and '0x1d78' not in identify_info[0]:  # 排除非dera ssd
                node_info.remove(node)

        # 获取服务器当前网络状态信息
        local = '10.0.4.1'  # 本地网关
        t_disk = '10.0.1.206'  # T盘所在服务器的IP地址
        internet = 'www.baidu.com'  # 外网
        net_bucket = [local, t_disk, internet]
        net_status = ['1', '1', '1']
        for ip in net_bucket:
            ping_command = 'ping {0} -c 2 -w 2'.format(ip)
            respond = os.popen(ping_command).readlines()
            for line in respond:
                if 'ttl' in line:
                    index = net_bucket.index(ip)
                    net_status[index] = '0'
                else:
                    pass
        net_status = ''.join(net_status)

        host_info = '{0}-{1}-{2}-{3}'.format(manufacturer, machine_type, cpus,
                                            mems)

        return host_info

    def genarate_current_trace():
        '''获取当前运行的脚本，机器状态，及ssd实例'''
        global node_info

        traces = []
        scripts = get_running_script()
        machine = get_machine_status()
        ssd = []
        for ssd_node in node_info:
            var_name = 'nvme%s' % str(node_info.index(ssd_node))
            locals()[var_name] = SSD(ssd_node)
            ssd.append(locals()[var_name])
        # 以nvme ssd作为标的物，生成trace
        for nvme in ssd:
            nvme.load()
            node = nvme.node
            running_script = ''

            if scripts:
                for script in scripts:
                    if 'ts_pwr.py' in script[
                            0]:  # 由于ts_pwr和ts_top带有掉电测试，所以是全局式的脚本，所有ssd均受影响，所以只要有一个SSD在运行该测试，则认为所有ssd均受此影响
                        running_script = script
                    elif 'ts_top.py' in script[0]:
                        running_script = script
                    elif node in script[1]:
                        running_script = script
                    else:
                        pass
            add_machine_and_script = dict([['machine', machine],
                                            ['script', running_script]])
            trace = nvme.info
            trace.update(add_machine_and_script)
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


def process_data(current_traces, old_traces):
    global now_time
    
    def send_info(data, server_ip='10.0.4.155'):
        global net_status

        if net_status != '000':  # 如果网络状态异常，则终止发送信息
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
        # 以第一个列表为基准，返回相对于第二个列表来说，增加的元素列表，和减少的元素列表
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
        '''对首次识别到的trace，筛选关键信息'''
        key_info = {
            'info_type': 'new_trace',  # 对于新卡，添加该键值以方便服务器端识别信息类型，做出相应处理    
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
        new_traces = []
        for sn in add_cards_sn:
            for trace in current_traces:
                if trace['SN'] == sn:
                    key_infomation = new_check(trace)  # 筛选关键信息进行发送
                    json_info = json.dumps(key_infomation)
                    send_info(json_info)  # 发送给服务器

        # json_info = json.dumps(new_traces)
        # send_info(json_info)  # 发送给服务器

        return

    def process_card_remove(remove_card):
        '''
        构建一条新的消息，格式如下，
        报告给中央服务器，该卡已经在机器上被移除了
        '''
        # ['R', timestamp, sn, err]
        global now_time
        new_traces = []
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
        return

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
                key_info = process_script_change(info, key_info)
            
            if not key_info:
                head_info['info_type': 'heartbeat']
            
            else:
                head_info['info_type': 'normal_update']
                head_info.update(key_info)
            
            json_info = json.dumps(key_info)
            send_info(json_info)

        return

    def indetify_card_status(current_traces, old_traces):
        current_cards_sn = [trace['SN'] for trace in current_traces if current_traces]  # 获取当前trace中ssd的names部分
        last_cards_sn = [trace['SN'] for trace in old_traces if old_traces]  # 获取上次扫描中ssd的names部分
        add_cards_sn = []
        remove_cards_sn = []
        normal_cards_sn = []

        add_cards_sn, remove_cards_sn = list_compare(current_cards_sn, last_cards_sn)  # 判断是否有丢卡，或新识别卡的情况发生
        normal_cards_sn = [x for x in current_cards_sn if x not in add_cards_sn]  # 既不是新添加的卡，也不包含弹出的卡

        if add_cards_sn:
            process_card_add(add_cards_sn)
        if remove_cards_sn:
            process_card_remove(remove_cards_sn)
        if normal_cards_sn:
            process_normal_mode(normal_cards_sn)
        return

    indetify_card_status(current_traces, old_traces)

    return


# ------ main logic ------ #
# 开机1分钟以内为准备阶段，不做检查
uptime_seconds, uptime = get_uptime()
while uptime_seconds < 60:
    time.sleep(1)
    uptime_seconds, uptime = get_uptime()

# 准备阶段结束，开始循环检查...
while True:
    global now_time
    now_time = timeStamp()

    current_traces, old_traces = get_data()
    process_data(current_traces, old_traces)

    with open('last_trace.json', 'w') as last_trace_obj:
        json.dump(current_traces, last_trace_obj)

    time.sleep(2)

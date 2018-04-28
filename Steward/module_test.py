#!/usr/bin/env python3
# Coding:UTF-8
import os
import re

#!/usr/bin/env python3
#coding:utf-8
import os
import re
import time
import pickle
from collections import Counter

'''
ssd测试过程中用到的类信息
'''

def list_to_dict(list_info, sep=':'):   # 输入列表， 以分隔符分隔， 输出字典
    '''将包含冒号的长字符串转换为字典格式'''
    list_temp = [] 
    
    for line in list_info:
        if line.count(sep) != 1:
            continue
        seprate_line = re.split(sep, line)
        seprate_line = [x.strip('/n').strip() for x in seprate_line]
        list_temp.append(seprate_line)
    
    dict_info = dict(list_temp)
    
    return dict_info


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
        get_pci_speed_cmd = "find /sys/* -name {0}|grep devices|cut -d '/' -f 6|xargs lspci -vvv -s|grep 'LnkSta:'|cut -d ' ' -f 2,4".format(self.diskname)
        pci_speed_info = os.popen(get_pci_speed_cmd).readlines()[0].strip('\n')
        pci_speed_processed = ''.join(pci_speed_info.split(','))
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


def get_running_script():   # 获取当前正在运行的脚本及参数，pid. 返回列表[[command1, args, pid]]
    '''获取当前正在运行的脚本及参数，pid. 返回列表[[command1, args, pid]]'''
    commands = []
    # 使用ps命令查看当前进程信息是否包含脚本名
    get_python3_script_fullname_cmd =  "ps -elf | grep -E 'HotPlug_NVMe_suite\.py|ts_.*\.py.*|runvdb.py.*'|grep -v grep"
    running_script_full_name = os.popen(get_python3_script_fullname_cmd).readlines()
    # 对返回的进程信息逐条进行拆分，拆分为命令本身和参数
    for cmd in running_script_full_name:
        # 使用正则表达式对进行信息进行拆分，以空格为分隔符
        cmd_tmp = re.split(' ', cmd)
        cmd_tmp = [x for x in cmd_tmp if x] # 去掉空字符
        for splited_cmd in cmd_tmp:
            command = []
            # 定位脚本名，及所在位置
            if '.py' in splited_cmd:
                pid = cmd_tmp[3]
                running_script_cmd = splited_cmd
                # 将脚本名后面的字符串作为参数，重新整合格式[command, args]
                running_script_args = ' '.join(cmd_tmp[cmd_tmp.index(splited_cmd)+1:]) # 截取脚本名后面的项，整合为空格分隔的字符串
                running_script_args = running_script_args.strip('\n')
                command = [running_script_cmd, running_script_args, pid]
                commands.append(command)
    return commands


def get_machine_status():   # 获取当前测试机信息，[厂商, 型号, cpu, 内存, nvme node, 开机时间, 网络状态]
    '''获取当前测试机信息，[厂商, 型号, cpu, 内存, nvme node, 开机时间, 网络状态]'''
    # 定义相关命令
    get_manufacturer_command = 'dmidecode -s system-manufacturer && dmidecode -s system-product-name'
    get_cpu_type_command = 'dmidecode -s processor-version'
    get_mem_count_command = 'dmidecode -t memory | grep Size: | grep -v No'
    get_men_type_command = "dmidecode -t memory | grep 'Type: DDR'|uniq"
    get_uptime_command = "cat /proc/uptime | cut -d ' ' -f 1"
    get_nvme_node_command = "ls /dev/nvme* | grep nvme.$"
    
    # 获取服务器厂商，型号信息
    machine_info = os.popen(get_manufacturer_command).readlines()
    machine_info = [x.strip('\n').strip() for x in machine_info]
    manufacturer, machine_type = machine_info
    # 获取服务器CPU信息
    cpu_info = os.popen(get_cpu_type_command).readlines()
    cpu_info = [x.strip('\n').strip() for x in cpu_info]
    cpus = ' '.join(['{0} * {1}'.format(str(x), str(y)) for x, y in Counter(cpu_info).items()])
    # 获取服务器内存信息
    mem_count = os.popen(get_mem_count_command).readlines()
    mem_count  = [x.strip('\n').strip() for x in mem_count]
    mem_type = os.popen(get_men_type_command).readlines()
    mem_type = [x.strip('\n').strip() for x in mem_type][0]
    mem_dict = Counter(mem_count)
    mems = ' '.join(['{0} * {1} {2}'.format(str(x), str(y), mem_type) for x, y in mem_dict.items()])
    # 获取dera nvme ssd字符设备信息
    node_info = os.popen(get_nvme_node_command).readlines()
    node_info = [x.strip('\n').strip() for x in node_info]
    for node in node_info:
        identify_info = os.popen("./nvme id-ctrl {0} | grep ^vid | cut -d ':' -f 2".format(node)).readlines()
        identify_info = [x.strip('\n').strip() for x in identify_info][0]
        if identify_info != '0x1d78':   # 排除非dera ssd
            node_info.remove(node)
    # 获取服务器开机时长信息
    uptime_seconds = os.popen(get_uptime_command).readlines()[0]
    uptime_seconds = float(uptime_seconds)
    m, s = divmod(uptime_seconds, 60)
    h, m = divmod(m, 60)
    uptime = "%02d:%02d:%02d" % (h, m, s)
    # 获取服务器当前网络状态信息
    local = '10.0.4.1' # 本地网关
    t_disk = '10.0.1.206' # T盘所在服务器的IP地址
    internet = 'www.baidu.com'  # 外网
    net_bucket = [local, t_disk, internet]
    net_status = ['1', '1', '1']
    for ip in net_bucket:
        ping_command = 'ping {0} -c 1 -w 1'.format(ip)
        respond = os.popen(ping_command).readlines()
        for line in respond:
            if 'ttl' in line:
                index = net_bucket.index(ip)
                net_status[index] = '0'
            else:
                pass
    net_status = ''.join(net_status)

    return [manufacturer, machine_type, cpus, mems, node_info, uptime, net_status]


def main():
    
    def timeStamp():
        now_time = datetime.datetime.now()
        readable_time = now_time.strftime('%Y-%m-%d_%H_%M_%S')
        return readable_time
    
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

    def genarate_current_trace(): # 
        '''获取当前运行的脚本，机器状态，及ssd实例'''
        traces = []
        scripts = get_running_script()
        machine = get_machine_status()
        ssd = []
        for ssd_node in machine[4]:
            var_name = 'nvme%s'%str(machine[4].index(ssd_node))
            locals()[var_name] = SSD(ssd_node)
            ssd.append(locals()[var_name])
        # 以nvme ssd作为标的物，生成trace
        for nvme in ssd:
            nvme.load()
            node = nvme.node
            running_script = ''
            
            if scripts:
                for script in scripts:
                    if 'ts_pwr.py' in script[0]:    # 由于ts_pwr和ts_top带有掉电测试，所以是全局式的脚本，所有ssd均受影响，所以只要有一个SSD在运行该测试，则认为所有ssd均受此影响
                        running_script = script
                    elif 'ts_top.py' in script[0]:
                        running_script = script
                    elif node in script[1]:
                        running_script = script
                    else:
                        pass
            add_machine_and_script = dict([['machine', machine], ['script', script]])
            trace = nvme.info
            trace.update(add_machine_and_script)
            traces.append(trace)
        return traces
    traces = genarate_current_trace()
    print(traces)
    return
main()
#!/usr/bin/env python3
# Coding:UTF-8
import os
import re

def load_ssd_info(node):
    diskname = re.split('/', node)[-1] # 获取nvme*
    ssd_info = {}
    # ------ 给ssd各项值赋值 ------ # 
    # 获取pci速度信息
    pci_speed_processed = get_pci_speed(diskname)
    ssd_info['pcispeed'] = pci_speed_processed

    # 获取boot 信息
    get_boot_drive_cmd = "df -h | grep -E '/boot$'"
    boot_drive_info = os.popen(get_boot_drive_cmd).readlines()[0]
    if diskname in boot_drive_info:
        boot = 'Master'
    else:
        boot = 'Slave'
    ssd_info['boot'] = boot

    # 获取dera info信息
    get_dera_info_cmd = "./nvme dera info {0}".format(node)
    dera_info = os.popen(get_dera_info_cmd).readlines()
    ssd.update(list_to_dict(dera_info))

    # 获取status信息并添加到字典
    get_dera_state_cmd = "./nvme dera state {0}".format(node)
    dera_state = os.popen(get_dera_state_cmd).readlines()
    ssd_info.update(list_to_dict(dera_state))

    return ssd_info

def genarate_current_trace():

    global node_info

    traces = []
    running_script = []    
    scripts = get_running_script()
    machine = get_machine_status()

    for script in scripts:
        if 'ts_pwr.py' in script[0] or 'ts_top.py' in script[0]:
            running_script = script
            break
    
    for node in node_info:
        if not running_script:
            
            
        ssd_info = load_ssd_info(node)



        ssd.append(ssd_info)




    # 以nvme ssd作为标的物，生成trace
    for ssd_info_dict in ssd:
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
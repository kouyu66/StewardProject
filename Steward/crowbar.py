#!/usr/bin/env python3
#coding:utf-8
import os
import re

'''
ssd测试过程中用到的类信息
'''


class SSD():
    '''一次模拟SSD的尝试'''
    def __init__(self, node):
        self.node = node
        self.diskname = re.split('/', self.node)[-1]
        # self.pcispeed = ''
        # self.boot = ''
        self.names = [] # [sn, mn, cap, boot, namespace]
        self.status = []    # [status, pcispeed, temps, cap_status, dev_status_up, current_pwr, ddr_err_bit, gpio_err_bit, pcie_voltage]
        self.vers = []  # [fw, fwld, fmt, uefi_driver]
        self.counters = []  # [powerCycles, powerOnHours, unsafe_shutdowns, media_err, nand_erase_err, nand_program_err, full_rebulid, raw_rebuild, pcie_uncorr_err, pcie_fatal_err, nand_init_fail, init_pcie_vot_low_cnt, rt_pcie_vot_low_cnt]
      
    def load(self):
        '''更新ssd状态信息'''
        # 获取pci速度信息
        get_pci_speed_cmd = "find /sys/* -name {0}|grep devices|cut -d '/' -f 8|xargs lspci -vvv -s|grep 'LnkSta:'|cut -d ' ' -f 2,4".format(self.diskname)
        pci_speed_info = os.popen(get_pci_speed_cmd).readlines()[0].strip('\n')
        pci_speed_processed = ''.join(pci_speed_info.split(','))
        pcispeed = pci_speed_processed
        # 获取boot 信息
        get_boot_drive_cmd = "df -h | grep -E '/boot$'"
        boot_drive_info = os.popen(get_boot_drive_cmd).readlines()[0]
        if self.diskname in boot_drive_info:
            boot = 'Master'
        else:
            boot = 'Slave'
        # 获取sn,mn,cap,format,fw信息
        get_dera_info_cmd = "./nvme dera info {0} | cut -d ':' -f 2".format(self.node)
        dera_info = os.popen(get_dera_info_cmd).readlines()
        dera_info = [x.strip('\n').strip() for x in dera_info]
        # 获取status信息并提取关键信息
        get_dera_state_cmd = "./nvme dera state {0} | cut -d ':' -f 2".format(self.node)
        dera_state = os.popen(get_dera_state_cmd).readlines()
        dera_state = [x.strip().strip('\n') for x in dera_state]

        if len(dera_info) == 7 and len(dera_state) == 66:
            sn, mn, namespace, cap, fmt, fw, linebreak = dera_info
            status = dera_state[0]
            powerCycles = dera_state[11]
            powerOnHours = dera_state[12]
            unsafe_shutdowns = dera_state[13]
            media_err = dera_state[14]
            temps = dera_state[18:26]
            cap_status = dera_state[28]
            dev_status_up = dera_state[30]
            nand_erase_err = dera_state[31]
            nand_program_err = dera_state[32]
            current_pwr = dera_state[34]
            full_rebulid = dera_state[37]
            raw_rebuild = dera_state[39]
            ddr_err_bit = dera_state[49]
            pcie_uncorr_err = dera_state[51]
            pcie_fatal_err = dera_state[52]
            nand_init_fail = dera_state[54]
            fwld = dera_state[55]
            uefi_driver = dera_state[56]
            gpio_err_bit = dera_state[59]
            pcie_voltage = dera_state[61]
            init_pcie_vot_low_cnt = dera_state[64]
            rt_pcie_vot_low_cnt = dera_state[65]
            
            self.names = [sn, mn, cap, boot, namespace]
            self.vers = [fw, fwld, fmt, uefi_driver]
            self.status = [status, pcispeed, temps, cap_status, dev_status_up, current_pwr, ddr_err_bit, gpio_err_bit, pcie_voltage]
            self.counters = [powerCycles, powerOnHours, unsafe_shutdowns, media_err, nand_erase_err, nand_program_err, full_rebulid, raw_rebuild, pcie_uncorr_err, pcie_fatal_err, nand_init_fail, init_pcie_vot_low_cnt, rt_pcie_vot_low_cnt]
        else:
            pass
        
        return

    
class Script():
    def __init__(self):
        self.scriptname = ''
        self.scriptargs = ''
        self.hours = 0
        self.starttime = ''
        self.estiend = ''
    def load(self):
        def get_script_name():
            get_python3_script_fullname_cmd =  "ps -elf | grep -E 'ts.*\.py.*|runvdb.py.*'|grep -v grep"
            running_script_full_name = os.popen(get_python3_script_fullname_cmd).readlines()
            

        def get_script_args()
        def get_script_time()
    # def update_fw():
    # def update_fwld():
    # def dump():

    #     return pci_speed_processed
    
    # def boot(self):
    #     get_boot_drive_cmd = "df -h | grep -E '/boot$'"
    #     boot_drive_info = os.popen(get_boot_drive_cmd).readlines()[0]

    #     if self.diskname in boot_drive_info:
    #         return 'Master'
    #     else:
    #         return 'Slave'

    # def name(self):
    #     '''name data format: [sn, mn, cap]'''
    #     get_static_info_cmd = "./nvme dera info {0} | grep -E 'SN|Model|Cap' | cut -d ':' -f 2".format(self.node)
    #     static_info = os.popen(get_static_info_cmd).readlines()
    #     static_info_processed = [x.strip('\n').strip() for x in static_info]
    #     return static_info_processed

    # def ver(self):
    #     '''version info data format:[format,fw,fwld,uefi]'''
    #     version_info = []
    #     get_fw_format_cmd = "./nvme dera info {0} | grep -E 'Format|Fw' | cut -d ':' -f 2".format(self.node)
    #     get_fwld_uefi_cmd = "./nvme dera state {0} | grep -E 'fw_loader|uefi_driver' | cut -d ':' -f 2".format(self.node)

    #     fw_format_info = os.popen(get_fw_format_cmd).readlines()
    #     fwld_uefi_info = os.popen(get_fwld_uefi_cmd).readlines()
    #     version_info.extend(fw_format_info)
    #     version_info.extend(fwld_uefi_info)

    #     versions = [x.strip('\n').strip() for x in version_info]
    #     return versions

    # def temp(self):
    #     '''temp info data format: [warning,critical,sensor1, sensor2, sensor3...sensor8]'''
    #     temp_info = []
    #     get_sensor_temp_cmd = "./nvme dera state {0}|grep -E 'temperature_sensor|warning_temperature_time|critical_composite_temperature_time'|cut -d ':' -f 2|cut -d ' ' -f 2".format(self.node)
    #     sensor_temp_info = os.popen(get_sensor_temp_cmd).readlines()
    #     temp_info = [int(x.strip('\n')) for x in sensor_temp_info]
    #     return temp_info

    # def power(self):
    #     '''power info date format: [powerCycle,powerOnHours,unsafeShutDown,currentPower,rt_pcie_volt_low_cnt]'''
    #     power_info = []
    #     get_power_cmd = "./nvme dera state {0}|grep -E 'power_cycles|power_on_hours|unsafe_shutdowns|current_power|rt_pcie_volt_low_cnt'|cut -d ':' -f 2|cut -d ' ' -f 2".format(self.node)
    #     power = os.popen(get_power_cmd).readlines()
    #     power_info = [int(x.strip('\n')) for x in power]
    #     return power_info
    
    # def err(self):
    #     '''err count info data format: [pcieUncorrectErr,pcieFatalErr,nandInitFail]'''
    #     err_info = []
    #     get_err_count_cmd = "./nvme dera state {0}|grep -E 'pcie_uncorr_err|pcie_fatal_err|nand_init_fail'|cut -d ':' -f 2|cut -d ' ' -f 2".format(self.node)
    #     error_count = os.popen(get_err_count_cmd).readlines()
    #     err_info = [int(x.strip('\n')) for x in error_count]
    #     return err_info
    
    # def dump(self):

# def checkRunningScript(frequence=3):
#     """
#     循环监控，每3秒一次反馈当前测试机脚本运行状态，并获取脚本名及运行参数
#     logic:
#     1. 读取上次检测到的 node信息，test trace信息. 
#     2. 获取当前node信息，test trace信息.
#     3. 对比三项信息进行判断：
#         1. 侦测test_trace变动(相对于上次)
#             1. 新增：添加到本次test trace信息表中
#             2. 减少：判断对应的SSD是否存在：
#                 1. 存在：
#                         1. 已标记为完成，删除trace.
#                         2. 未标记为完成，标记该trace测试完成，发送test_complete信号，添加到本次test_trace信息表中.
#                 2. 不存在: 检查上次trace是否标记为测试完成：
#                         1. 是： 认为本次丢卡为卡弹出动作，与测试无关，发送card_eject信号，删除trace.
#                         2. 否： 测试过程中卡丢失，发送test_fail信号，删除trace.
#         2. 更新时间戳
#     4. 将本次检查写入磁盘
#     5. 3s后跳至第一步
#     """
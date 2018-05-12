#!/usr/bin/env python3
# Coding:UTF-8
import os
import re

def SSD(node):
    diskname = re.split('/', self.node)[-1] # 获取nvme*
    ssd_info = {}
# ------ 给ssd各项值赋值 ------ #
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
    get_dera_info_cmd = "./nvme dera info {0}".format(diskname)
    dera_info = os.popen(get_dera_info_cmd).readlines()
    ssd.update(list_to_dict(dera_info))

    # 获取status信息并添加到字典
    get_dera_state_cmd = "./nvme dera state {0}".format(self.node)
    dera_state = os.popen(get_dera_state_cmd).readlines()
    self.info.update(list_to_dict(dera_state))       
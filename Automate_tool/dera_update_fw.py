#!/usr/bin/env python3
# 基于固定的firmware存放路径，自动更新dera firmware
# 支持批量更新
# 支持指定版本更新
# 支持更新fwslot或者boot + cc
# 判断更新状态
import os
import re

# 定义变量
global ssd_info
global command_pool
ssd_info = {}
command_pool = []

# 流程概述
# 1. 检查升级环境
    # nvme工具检查；版本信息获取并打印
    # T盘挂载，检查任意一个firmware路径是否可访问
# 2. 获取卡基本信息
# 3. 确定升级命令
# 4. 下发命令
# 5. 检查返回值

def env_check():
    '''检查nvme工具是否存在，并打印版本号'''
    if not os.path.exists('nvme'):
        print('- nvme tool not found. copy tools to current folder...')
        return_code = os.system('cp /system_repo/tools/nvme/nvme .')
        if return_code == 0:
            print('* nvme tool get successfully.')
        else:
            print('* warning: nvme tool get failed, please check network to drive T')
            return 1
    p_nvme_ver = (os.popen('./nvme version').read()).strip()
    print(p_nvme_ver)
    return 0

def ssd_info_check():
    '''获取nvme ssd的基本信息，返回一个字典'''
    global ssd_info
    get_info_raw_cmd = './nvme dera info | grep nvme'

    info_raw_list = os.popen(get_info_raw_cmd).readlines()

    if not info_raw_list:
        print('* warning: no nvme devices found.')
        return 1
    
    for info in info_raw_list:
        nvme = re.search(r'nvme\d{1,2}', info).group()
        mn_search = re.search(r'\S{6}-\S{5}-\S{2}', info)
        if not mn_search:  # 用于处理非dera ssd的状况：
            continue
        mn = mn_search.group()
        ssd_info[nvme] = mn
    ssd_num = len(ssd_info)
    if ssd_num == 0:
        print('- no dera nvme devices found. update programe will exit.')
        return 1

    print('- {0} dera nvme devices info found:'.format(ssd_num))
    for key, value in ssd_info.items():
        print('  {0} : {1}'.format(key, value))
    return ssd_info

def process_bootable_drive():
    '''确认启动盘与本次升级动作是否相关'''
    get_boot_disk = "df -h | grep -E '/boot$'"
    boot_info = os.popen(get_boot_disk).read()
    
    boot_drive_obj = re.search(r'nvme\d{1,2}', boot_info)
    if boot_drive_obj:
        nvme = boot_drive_obj.group()
        if nvme in ssd_info.keys():
            return nvme
    return    # 启动盘为非nvme设备，无需处理

def update_command(ssd_info):
    global command_pool
    command_dict = {}
    update_mode = input('\n input 1 for common update\n input 2 for debug firmware upate\n > ')

    if update_mode is '1':
        firmware_ver = input(' input firmware version, like "108"\n > ')
        
        print('- scaning dera ssd type...')
        path_dict = {
        'P34UTR-01T0U-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/UD2/OUTZ3{0}/'.format(firmware_ver),
        'P34UTR-01T0H-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/AIC/OATZ3{0}/'.format(firmware_ver),
        'P34UTR-01T6U-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/UD2/OUTG9{0}/'.format(firmware_ver),
        'P34UTR-01T6H-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/AIC/OATG9{0}/'.format(firmware_ver),
        'P34UTR-02T0U-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/UD2/OUTZ9{0}/'.format(firmware_ver),
        'P34UTR-02T0H-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/AIC/OATZ9{0}/'.format(firmware_ver),
        'P34UTR-03T2U-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/UD2/OUTGA{0}/'.format(firmware_ver),
        'P34UTR-03T2H-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/AIC/OATGA{0}/'.format(firmware_ver),
        'P34UTR-04T0U-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/UD2/OATZA{0}/'.format(firmware_ver),
        'P34UTR-04T0H-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/AIC/OATZA{0}/'.format(firmware_ver),
        'P34UTR-06T4U-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B17/UD2/OATUA{0}/'.format(firmware_ver),
        'P34UTR-06T4H-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B17/AIC/OATUA{0}/'.format(firmware_ver)
        }

    for key, value in ssd_info.items():
        if value in path_dict.keys():
            command_dict[key] = path_dict[value]
        else:
            print('* warning: unknown dera mn found, update operation will not work on this drive: {0} {1}'.format(key,value))
            pass
    
    update_mode = input(' select update mode:\n 1. boot + cc\n 2. boot + drivecfg\n 3. slot \n > ')
    bootable_drive = process_bootable_drive()
    
    for key, value in command_dict.items():
        if key == bootable_drive and update_mode is '1' or update_mode is '2':
            boot_drive_select = input('* warning: boot drive will update firmware slot to avoid data loss. press Enter to continue, or press N if you want to wipe out boot drive.\n > ')
            if not boot_drive_select == 'N' and not boot_drive_select == 'n':
                command1 = './nvme dera update-fw -y /dev/{0} -f {1}{2}'.format(key, value, 'fwslot*')
                command_pool.append(command1)

        if update_mode is '1':
            command1 = './nvme dera update-fw -y /dev/{0} -f {1}{2}'.format(key, value, 'boot*')
            command2 = './nvme dera update-fw -y /dev/{0} -f {1}{2}'.format(key, value, 'cc*')
            command_pool.append(command1)
            command_pool.append(command2)
        elif udpate_mode is '2':
            command1 = './nvme dera update-fw -y /dev/{0} -f {1}{2}'.format(key, value, 'boot*')
            command2 = './nvme dera update-fw -y /dev/{0} -f {1}{2}'.format(key, value, 'drive*')
            command_pool.append(command1)
            command_pool.append(command2)
        elif update_mode is '3':
            command1 = './nvme dera update-fw -y /dev/{0} -f {1}{2}'.format(key, value, 'fwslot*')
            command_pool.append(command1)
    return

def update_fw(command):
    step1 = os.popen(command).read()
    if not 'Success' in step1:
        print('* Warning: Command Execute Fail! \n {0}'.format(command))
    return
    
env_check()
ssd_info_check()
bootable_drive = process_bootable_drive()
update_command(ssd_info)
for command in command_pool:
    update_fw(command)

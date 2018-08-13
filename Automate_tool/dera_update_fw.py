#!/usr/bin/env python3
# -*- coding:utf-8 -*
# Author: kouxinyu
# Email: kouyu66@163.com
# Version: 0.9.2
# 采用应答式输入，多线程批量升级机器上连接的Dera SSD固件版本
# linux only

import os
import re
import threading

# 定义变量
global ssd_info         # 定义设备名与mn号对应的全局字典
global command_pool1    # 定义命令池1
global command_pool2    # 定义命令池2
global command_pool3    # 定义命令池3
global command_pool4    # 定义命令池4
global return_code      # 定义返回值列表，以便于统一打印
ssd_info = {}
command_pool1 = []
command_pool2 = []
command_pool3 = []
command_pool4 = []
return_code = []


def env_check():
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

def ssd_info_check():
    '''获取nvme ssd的基本信息，返回一个字典'''
    global ssd_info
    get_info_raw_cmd = './nvme dera info | grep nvme'

    info_raw_list = os.popen(get_info_raw_cmd).readlines()

    if not info_raw_list:
        print('* warning: no nvme devices found.')
        exit()
    
    for info in info_raw_list:
        mn_search = re.search(r'\S{6}-\S{5}-\S{2}', info)   #逐行检索dera mn号的特征
        if not mn_search:                                   # 非dera ssd被抛弃
            continue
        mn = mn_search.group()                              # 获取dera mn编号
        nvme = re.search(r'nvme\d{1,2}', info).group()      # 检索设备号 nvme1 - nvmen
        ssd_info[nvme] = mn                                 # 将设备号与对应的mn号写入全局字典

    dera_ssd_num = len(ssd_info)
    if dera_ssd_num == 0:
        print('- no dera nvme devices found. update programe will exit.')
        exit()

    print('- {0} dera nvme devices info found:'.format(dera_ssd_num))
    for key, value in ssd_info.items():
        print('  {0} : {1}'.format(key, value))
    return ssd_info

def process_bootable_drive():
    '''确认启动盘与本次升级动作是否相关'''
    get_boot_disk = "df -h | grep -E '/boot$'"
    boot_info = os.popen(get_boot_disk).read()
    
    boot_drive_obj = re.search(r'nvme\d{1,2}', boot_info)   # 使用正则表达式获取系统盘的设备号
    if boot_drive_obj:
        nvme = boot_drive_obj.group()
        if nvme in ssd_info.keys():                         # 判断系统盘是否为dera ssd
            return nvme
    return                                                  # 启动盘为非nvme设备，无需处理

def update_command(ssd_info):
    '''确定nvme设备与升级命令的对应关系，根据升级文件的不同，生成四个列表，并处理主盘firmware升级的情况'''
    global command_pool1
    global command_pool2
    global command_pool3
    global command_pool4
    command_dict = {}
    update_mode = input('\n input 1 for common update\n input 2 for debug firmware update\n > ')

    if update_mode is '1':  # common update模式下，根据mn号自动匹配T盘固定路径下的firmware文件路径
        firmware_ver = input(' input firmware version, like "108"\n > ')
        path_dict = {
        'P34UTR-01T0U-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/UD2/OUTZ3{0}/'.format(firmware_ver),
        'P34UTR-01T0H-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/AIC/OATZ3{0}/'.format(firmware_ver),
        'P34UTR-01T6U-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/UD2/OUTG9{0}/'.format(firmware_ver),
        'P34UTR-01T6H-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/AIC/OATG9{0}/'.format(firmware_ver),
        'P34UTR-02T0U-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/UD2/OUTZ9{0}/'.format(firmware_ver),
        'P34UTR-02T0H-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/AIC/OATZ9{0}/'.format(firmware_ver),
        'P34UTR-03T2U-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/UD2/OUTGA{0}/'.format(firmware_ver),
        'P34UTR-03T2H-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/AIC/OATGA{0}/'.format(firmware_ver),
        'P34UTR-04T0U-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/UD2/OUTZA{0}/'.format(firmware_ver),
        'P34UTR-04T0H-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B16/AIC/OATZA{0}/'.format(firmware_ver),
        'P34UTR-06T4U-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B17/UD2/OUTUA{0}/'.format(firmware_ver),
        'P34UTR-06T4H-ST':'/system_repo/tools/fwsmg/EDISON/v{0}/B17/AIC/OATUA{0}/'.format(firmware_ver)
        }
        for key, value in ssd_info.items():
            if value in path_dict.keys():
                command_dict[key] = path_dict[value]
            else:
                print('* warning: unknown dera mn found, update operation will not work on this drive: {0} {1}'.format(key,value))
                pass

    elif update_mode is '2':    # debug firmware模式下，不匹配路径，直接使用用户输入的路径作为所有ssd的升级路径
        # print('* Warning: all ssd will use the same debug firmware.')
        # firmware_path = input(' input debug firmware path. like /debug/firmware/RATG9113/ \n > ')
        # for key in ssd_info.keys():
        #     command_dict[key] = firmware_path
        firmware_path = input(" input firmware parrent path, like /debug/firmware/RUTZ3110, input'/debug/firmware/'\n* warning: make sure the firmware folder named like RUTZ3*\n > ")
        path_dict = {
        'P34UTR-01T0U-ST':'{0}RUTZ3*/'.format(firmware_path),
        'P34UTR-01T0H-ST':'{0}RATZ3*/'.format(firmware_path),
        'P34UTR-01T6U-ST':'{0}RUTG9*/'.format(firmware_path),
        'P34UTR-01T6H-ST':'{0}RATG9*/'.format(firmware_path),
        'P34UTR-02T0U-ST':'{0}RUTZ9*/'.format(firmware_path),
        'P34UTR-02T0H-ST':'{0}RATZ9*/'.format(firmware_path),
        'P34UTR-03T2U-ST':'{0}RUTGA*/'.format(firmware_path),
        'P34UTR-03T2H-ST':'{0}RATGA*/'.format(firmware_path),
        'P34UTR-04T0U-ST':'{0}RUTZA*/'.format(firmware_path),
        'P34UTR-04T0H-ST':'{0}RATZA*/'.format(firmware_path),
        'P34UTR-06T4U-ST':'{0}RUTUA*/'.format(firmware_path),
        'P34UTR-06T4H-ST':'{0}RATUA*/'.format(firmware_path)
        }
        for key, value in ssd_info.items():
            if value in path_dict.keys():
                command_dict[key] = path_dict[value]
            else:
                print('* warning: unknown dera mn found, update operation will not work on this drive: {0} {1}'.format(key,value))
                pass
    
    update_file = input(' select update mode:\n 1. boot + cc\n 2. boot + drivecfg\n 3. slot \n > ')
    bootable_drive = process_bootable_drive()
    
    for key, value in command_dict.items():
        if key == bootable_drive and update_file != '3':    # 处理升级firmware操作遇到主盘的情况
            message = '''* warning: Online Dera Boot Drive Detected.
* boot drive will not be update by default. press Enter to continue.
* or press u to update fwslot to avoid data loss, but firmware loader will not be update.
* or press d to update what you chouse and wipe out boot drive.\n > '''
            boot_drive_select = input(message)
            if boot_drive_select == 'u':    #   升级firmware slot，避免主盘数据丢失
                command4 = './nvme dera update-fw -y /dev/{0} -f {1}{2}'.format(key, value, 'fwslot*')
                command_pool4.append(command4)
                continue                    # 不再针对该盘添加升级命令到其他command_pool
            elif not boot_drive_select:
                continue                    # 用户输入为空时，对系统盘不进行升级操作

        if update_file is '1':
            command1 = './nvme dera update-fw -y /dev/{0} -f {1}{2}'.format(key, value, 'boot*')
            command3 = './nvme dera update-fw -y /dev/{0} -f {1}{2}'.format(key, value, 'cc*')
            command_pool1.append(command1)
            command_pool3.append(command3)
        elif update_file is '2':
            command1 = './nvme dera update-fw -y /dev/{0} -f {1}{2}'.format(key, value, 'boot*')
            command2 = './nvme dera update-fw -y /dev/{0} -f {1}{2}'.format(key, value, 'drive*')
            command_pool1.append(command1)
            command_pool2.append(command2)
        elif update_file is '3':
            command4 = './nvme dera update-fw -y /dev/{0} -f {1}{2}'.format(key, value, 'fwslot*')
            command_pool4.append(command4)
    return

def update_fw(command):
    '''执行firmware升级动作，判断是否成功，并把结果汇总到全局列表'''
    global return_code
    step1 = os.popen(command).read()
    command_split = re.split(r'[/ ]', command)
    dev_name = re.search(r'nvme\d{1,2}', command).group()
    firmware_file = command_split[-1]

    if not 'Success' in step1:
        results = '* {0}: firmware {1} update fail.'.format(dev_name, firmware_file)
        print(command)
    else:
        results = '- {0}: firmware {1} update successful.'.format(dev_name, firmware_file)
    return_code.append(results)
    return
    
def multiThread(funcname, listname):
    """以列表中元素作为参数，列表元素数作为线程个数，多线程执行指定函数
    阻塞，当所有线程执行完成后才继续主线程"""
    threadIndex = range(len(listname))
    threads = []
    for num in threadIndex :
        t = threading.Thread(target=funcname, args=(listname[num],))
        threads.append(t)
    for num in threadIndex:
        threads[num].start()
    for num in threadIndex:
        threads[num].join()
    return

def print_results():
    '''打印升级状态文本'''
    global return_code
    return_code.sort()
    print('\n')                 # nvme 工具会自动打印‘.’ 为了便于观察结果，故输入换行符
    for info in return_code:    # 顺序打印所有线程的返回值
        print(info)
    return

def path_verify(command_pool):
    for command in command_pool:
        fw_file = re.split(r' ', command)[-1]
        dev_name = re.search(r'nvme\d{1,2}', command).group()        
        fw_parrent_folder = '/'.join(re.split('/', fw_file)[0:-1])
        if not os.path.exists(fw_parrent_folder):
            print('* {0}: firmware {1} update fail: file not found.'.format(dev_name, fw_file))
            command_pool.remove(command)
        else:
            pass
    return


env_check()
ssd_info_check()
bootable_drive = process_bootable_drive()
update_command(ssd_info)
command_pool_list = [command_pool1, command_pool2, command_pool3, command_pool4]
for command_pool in command_pool_list:
    # path_verify(command_pool) # debug firmware由于使用了通配符，不支持该检查
    multiThread(update_fw, command_pool)
print_results()

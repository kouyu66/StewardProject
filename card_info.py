import os
import time
import steward_lib

"""
NVME命令群发工具
1. 从文本文件获取ip地址池，存储到列表；
2. 每个ip地址开启一个线程，发送一个ping命令，根据返回的ttl值判断该ip地址所在机器的操作系统
3. 将每个ip地址对应的操作系统存储到不同的列表中
4. 登陆到每台linux操作系统的机器上，执行拷贝命令，拷贝nvme工具到/目录， 并处理报错信息
5. 执行nvme工具命令，获取返回值，存储到列表
6. 优化打印格式，将结果输出到屏幕
"""
# global variable
linux_machine_pool = []
windows_machine_pool = []
unknow_machine_pool = []
ip_card = []

# function module
def get_ip_list(file='ip_list.txt'):
    """将文本文件转换为python列表"""
    
    ip_list = steward_lib.filetoList(file)
    # ip_list = ['10.0.4.' + str(x) for x in range(1,255)] # 全网段
    return ip_list

def ping_host(ip,timeout=500):
    """ping 一台主机，如果ping通，根据返回ttl值判断操作系统类型（win/linux），如果没通，连续ping，直到超时（seconds.）"""
    
    os_info = steward_lib.delay_ping(ip, timeout)

    # for this script only
    if os_info[1] is 'linux':
        linux_machine_pool.append(os_info[0])
    elif os_info[1] is 'windows':
        windows_machine_pool.append(os_info[0])
    else:
        unknow_machine_pool.append(os_info[0])
    return os_info

# def card_identify(ip):  # [ip,[sn]]
#     copy_result = steward_lib.ssh_command(ip,'cp /system_repo/tools/nvme/nvme /')
#     sn = []
#     if not copy_result:
#         time.sleep(1)
#         ssd_info = steward_lib.ssh_command(ip, '/nvme dera info')
#         for ssd in ssd_info:
#             card_sn = steward_lib.findString(ssd, '\d{6}\w{1}\d{3}\w{2}\d{4}')
#             if card_sn:
#                 card_sn = card_sn[0]
#             sn.append(card_sn)
#     else:
#         sn = 'nvme tools copy error'
#     ip_card.append([ip,sn])
#     return
def main():
    iplist = get_ip_list()
    steward_lib.multiThread(ping_host,iplist)

    # while len(linux_machine_pool) + len(windows_machine_pool) + len(unknow_machine_pool) != 56:
    # print(linux_machine_pool)
    for x in linux_machine_pool:
        print(x)
    return
main()
#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import time
import steward_lib


def current_status(ip):
    # status = [ip, code]
    #   code = 0: no running script
    #   code = 2: edge situation, equal to offline
    #   code = 3: win plantform, not support now

    ostype = steward_lib.knowOSpyPing(ip)
    runningScript = []
    if ostype is 'linux':
        # raw_runningScript = steward_lib.ssh_command(ip, "ps -elf |grep -v 'grep'|grep '\./ts_.*'")
        try:
            raw_runningScript = steward_lib.ssh_command(ip, "ps -elf |grep -v 'grep'|grep -E '\./ts_.*|\./runio.*'")
            if not raw_runningScript:
            # time.sleep(7)
            # raw_runningScript = steward_lib.ssh_command(ip, "ps -elf |grep -v 'grep'|grep '\./.*\.py.*'")
            # if not raw_runningScript:
                runningScript = 0
            else:
                listed_runningScript = [steward_lib.findString(str,'\./.*\.py')for str in raw_runningScript]
                for x in listed_runningScript:
                    for y in x:
                        runningScript.append(y)
        except TimeoutError or AttributeError:
            runningScript = 2

    elif ostype is 'windows':
        runningScript = 3
    else:
        runningScript = 2
    status = [ip, runningScript]
    status_list.append(status)
    return

def highLightPrint(list):
    
    idle_list = []
    running_list = []
    offline_list = []
    win_list = []

    for trace in list:
        if trace[1] == 0:
            idle_list.append(trace[0])
        elif trace[1] == 2:
            offline_list.append(trace[0])
        elif trace[1] == 3:
            win_list.append(trace[0])
        else:
            running_list.append(trace)
    print(steward_lib.timeStamp())
    print('-' * 40)

    if idle_list:
        for ip in idle_list:
            print('! IDLE  {0}'.format(ip))
    if offline_list:
        for ip in offline_list:
            print('Offline {0}'.format(ip))
    if  win_list:
        for ip in win_list:
            print('Dont Support Win {0}'.format(ip))
    if running_list:
        for trace in running_list:
            print('{1} {0}'.format(trace[0],trace[1]))
    print('*' * 40)

    return
 
def main():
    while True:
        global status_list
        status_list  = []
        iplist = steward_lib.filetoList('ip_list.txt')
        steward_lib.multiThread(current_status, iplist)
        highLightPrint(status_list)
        time.sleep(60)
main()
    
# while True:
#     print('-------------------')
#     print(steward_lib.timeStamp())
#     print('-------------------')
#     main()
#     print('===================\n')
#     time.sleep(60)

# inforGet() [ip, [Card infor ], [running script], [last 3 line log_infor], [pci_infor]]
# def GetInfor(ip):

#     ostype = steward_lib.knowOSpyPing(ip)
#     card_info = []
#     running_script = []
#     log_infor = []
#     pci_infor = []

#     raw_str_running_script = steward_lib.ssh_command(ip, "ps -elf |grep -v 'grep'|grep '\./.*\.py.*'")
#     if raw_str_running_script:
#         for script in raw_str_running_script:
#             running_script.append(script[0])
#     else:
#         raw_pci_infor = steward_lib.ssh_command(ip, "ls /dev/nvme*")
#         for pci in raw_pci_infor:
#             pci_infor.append(pci[0])

#         raw_card_infor = steward_lib.ssh_command(ip, "/ge/auto/nvme dera info")            
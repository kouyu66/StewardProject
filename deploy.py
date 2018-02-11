#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import threading
import time
import steward_lib
import sys

global ip_list
global machine_info
ip_list = []
machine_info = []
# def machineSelect(filename):
#     selectFrom(filename)    #选择模式，从列表中选择（适用于多台机器），指定ip地址（适用于少量机器）
#     machineCheck(machine_ip_list)    #检查用户选择的机器是否处于正常通讯状态
#         connectionCheck()   #联通状态检查
#         deviceCheck()       #待测设备检查
#         runningScriptCheck()#运行中的脚本检查，rc文件检查
#         dumpLog()           #保存测试机上次测试的log文件
#         delayOps(ip,command,triger)#满足条件时运行命令
#             triger()
#     outPut()
#     dataFormat = [ip,ssd_mn,status,]
#     return 
def selectFrom(ip_list_file):
    if len(sys.argv) > 1:
        ip_list.extend(sys.argv[1:])
    else:
        ip_list.extend(steward_lib.filetoList(ip_list_file))
        # ip_pool = steward_lib.filetoList(ip_list_file)
        # if ip_pool:
        #     ip_list = steward_lib.selectFromList(ip_pool)
    return ip_list

def machineCheck(ip):
    # machine_status format: [ip, linux, device, runningscript]
    machine_status = [ip, 9, 9, 9]
    
    
    def connectionCheck(ip):
        connection = steward_lib.knowOSpyPing(ip)
        if not connection:
            return 1
        elif connection == 'linux':
            return 0
        else:
            return 2
    def deviceCheck(ip):    # connectionCheck 返回 1 时执行检查
        raw_output = steward_lib.ssh_command(ip, "/ge/auto/nvme dera info | grep '/'")
        if raw_output:
            for str in raw_output:
                sn = steward_lib.findString(str, '\d{6}A\d{3}NN\d{4}')
            return sn
        else:
            return 0
    def runningScriptCheck(ip): # 检查测试机上是否有正在运行的脚本
        raw_output = steward_lib.ssh_command(ip, "ps -elf |grep -v 'grep'|grep -E '\./ts_.*|\./runio.*'")
        if not raw_output:
            return 0
        else:
            runningScript = [steward_lib.findString(str,'\./.*\.py')for str in raw_output]
            return runningScript
    
    
    connection = connectionCheck(ip)
    if connection == 0:
        running = runningScriptCheck(ip)
        device = deviceCheck(ip)
        
        machine_status[1] = connection
        machine_status[2] = device
        machine_status[3] = running
    elif connection == 1:
        machine_status[1] = connection
        machine_status[2] = 'n/a'
        machine_status[3] = 'n/a'
        
    machine_info.append(machine_status)
    return

def multiThread(funcname, list):
    """以列表中元素作为参数，列表元素数作为线程个数，多线程执行指定函数"""
    threadIndex = range(len(list))
    threads = []
    for num in threadIndex :
        t = threading.Thread(target=funcname, args=(ip_list[num],))
        threads.append(t)
    for num in threadIndex:
        threads[num].start()
    for num in threadIndex:
        threads[num].join()
    return


selectFrom('ip_list.txt')
multiThread(machineCheck, ip_list)
print(machine_info)

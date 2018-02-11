import subprocess
import time
import re
import os
import datetime
import threading
import paramiko

# def checkConnection(ip):
#     """check connection to input ip address."""
#     if subprocess.call('ping -n 1 -w 1 {0}'.format(ip)) == 0:
#         print('{0} online.'.format(ip))
#         return 0
#     else:
#         retry = subprocess.call('ping -n 1 -w 1 {0}'.format(ip))
#         if retry != 0:
#             print('{0} offline.'.format(ip))
#             return 1
#         else:
#             print('{0} online.'.format(ip))
#             return 0
def ssh_command(ip, command, username='root', password='Password1'):
    s = paramiko.SSHClient()
    s.load_system_host_keys
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        s.connect(ip, 22, username, password)
    except paramiko.ssh_exception.AuthenticationException: 
        username = 'dera'
        s.connect(ip, 22, username, password)
        ssh = s.invoke_shell()
        time.sleep(0.1)
        ssh.send('su - \n')
        time.sleep(1)
        # buff = ''
        # while not buff.endswith('Password: '):
        #     resp = str(ssh.recv(9999))
        #     buff += resp
        ssh.send(password)
        ssh.send('\n')
        
    # except Exception:
        # return
    result = []
    stdin, stdout, stderr = s.exec_command(command)
    result = stdout.readlines()
    # if not result:
    #     time.sleep(7)
    #     stdin, stdout, stderr = ssh.exec_command(command)
    #     result = stdout.readlines()
    s.close()
    return result

def findString(string,reg):
    regObj = re.compile(reg)
    match = regObj.findall(string)
    if match:
        return match
    else:
        return

def knowOSpyPing(ip):
    """determine the OS type by ping command"""
    command = 'ping -n 1 -w 1 {0}'.format(ip)
    run = os.popen(command)
    info = run.readlines()
    for line in info:
        match = findString(line, 'TTL=\d{2,}$') # 依赖steward_lib函数库,用正则表达式获取ping命令返回的ttl值
        if match:
            ttl = int(match[0][4:]) # 将ttl值转换为数字
            if 64 <= ttl <= 128:    # 依据ttl值判断操作系统, 默认值64为linux操作系统, 默认值为128为windwos操作系统.
                return 'windows'
            else:
                return 'linux'
    return

def delay_ping(ip,timeout=70):
    """连续ping目标主机，直到ping通或超时为止，返回[ip,os]列表，如果没通，os返回值为'unknown'"""
    os = knowOSpyPing(ip)
    starttime = datetime.datetime.now()
    while not os:
        time.sleep(0.5)
        os = knowOSpyPing(ip)
        endtime = datetime.datetime.now()
        if (endtime - starttime).seconds > timeout:
            if not os:
                os = 'unknown'
            break
    return [ip,os]

def filetoList(filePath):
    '''将文本文件逐行读取到列表,输入文件路径,返回列表'''
    machineList = []
    with open(filePath) as machinePoolObj:
        machines = machinePoolObj.readlines()
    for machine in machines:
        machine = machine.strip('\n')
        machineList.append(machine)
    return machineList

def timeStamp():
    now_time = datetime.datetime.now()
    readable_time = now_time.strftime('%Y-%m-%d %H:%M:%S')
    return readable_time

def selectFromList(list):
    '''输入列表，根据用户输入序号打印用户选择的项并返回用户选择项的列表，用户输入支持逗号和空格'''
    for item in list:
        print((list.index(item) + 1), item)
    
    index_list = []
    
    while not index_list:
        user_select = input('input index number to choose item, sepret by space.\n')
        if not user_select:
            print('None Select.')
            return
        elif ' ' in user_select:
            raw_index_list = user_select.split(' ')
        elif ',' in user_select:
            raw_index_list = user_select.split(',')
        else:
            raw_index_list = user_select.split()
        for str in raw_index_list:
            try:
                index_list = [int(x) for x in raw_index_list]
                for index in index_list:
                    temp_index = index - 1
                    if temp_index not in range(len(list)):
                        print('One or more select out of range.')
                        index_list = []
            except Exception:
                print('Input the INDEX NUMBER, sepreted by space or comma if multipal.')
                index_list = []
    
    user_select_item = [list[index-1] for index in index_list]
    print('Selected Item:')
    for item in user_select_item:
        print(item)
    return user_select_item

def multiThread(funcname, listname):
    """以列表中元素作为参数，列表元素数作为线程个数，多线程执行指定函数"""
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

def multiThreadDeamon(funcname, listname):
    threadIndex = range(len(listname))
    threads = []
    for num in threadIndex :
        t = threading.Thread(target=funcname, args=(listname[num],), daemon=True)
        threads.append(t)
    for num in threadIndex:
        threads[num].start()
    return

def mnToModule(pn_number):
    match_D5450_AIC = findString(pn_number, 'MMM-\w{4}H')
    if match_D5450_AIC:
        return 'D5450 AIC'
    match_D5450_U_2 = findString(pn_number, 'MMM-\w{4}U')
    if match_D5450_U_2:
        return 'D5450 U.2'
    match_D5430_AIC = findString(pn_number, 'MMR-\w{4}H')
    if match_D5430_AIC:
        return 'D5430 AIC'
    match_D5430_U_2 = findString(pn_number, 'MMR-\w{4}U')
    if match_D5430_U_2:
        return 'D5430 U.2'
    match_D5436_AIC = findString(pn_number, 'USR-\w{4}H')
    if match_D5436_AIC:
        return 'D5436 AIC'
    match_D5437_AIC = findString(pn_number, 'UTR-\w{4}H')
    if match_D5437_AIC:
        return 'D5437 AIC'
    else:
        return

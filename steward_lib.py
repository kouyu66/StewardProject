# -*- coding: UTF-8 -*-
import subprocess
import time
import re
import os
import datetime
import threading
# import paramiko

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
# #             return 0
# def ssh_command(ip, command, username='root', password='Password1'):
#     s = paramiko.SSHClient()
#     s.load_system_host_keys
#     s.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#     try:
#         s.connect(ip, 22, username, password)
#     except paramiko.ssh_exception.AuthenticationException: 
#         username = 'dera'
#         s.connect(ip, 22, username, password)
#         ssh = s.invoke_shell()
#         time.sleep(0.1)
#         ssh.send('su - \n')
#         time.sleep(1)
#         # buff = ''
#         # while not buff.endswith('Password: '):
#         #     resp = str(ssh.recv(9999))
#         #     buff += resp
#         ssh.send(password)
#         ssh.send('\n')
        
#     # except Exception:
#         # return
#     result = []
#     stdin, stdout, stderr = s.exec_command(command)
#     result = stdout.readlines()
#     # if not result:
#     #     time.sleep(7)
#     #     stdin, stdout, stderr = ssh.exec_command(command)
#     #     result = stdout.readlines()
#     s.close()
#     return result

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

def get_os_name():
    OS_type = 'null'
    sysstr = platform.system()
    if (sysstr == "Windows"):
        OS_type = 'Windows'
    elif (sysstr == "Linux"):
        Resf = ()
        cmdf = 'cat /proc/version'
        Resf = sys_cmd_out_noprint(cmdf)
        if Resf[0] == 0:
            if "Red Hat" in Resf[1][0]:
                cmds = 'cat /etc/redhat-release'
                Ress = sys_cmd_out_noprint(cmds)
                if Ress[0] == 0:
                    if "CentOS" in Ress[1][0]:
                        OS_type = 'CentOS'
                    elif "Red Hat" in Ress[1][0]:
                        OS_type = 'RHEL'
                    else:
                        return 1
                else:
                    return 2
            elif "Ubuntu" in Resf[1][0]:
                OS_type = 'Ubuntu'
            elif "SuSE" in Resf[1][0]:
                OS_type = 'SLES'
            elif "Debian" in Resf[1][0]:
                OS_type = 'Debian'
            else:
                return 3
        else:
            return 4
    return OS_type

def _build_rc_linux(argv=[]):
    '''
    Build startup file into system start up task
    :param argv: The command string
    :return:
    '''
    rc_name = os.path.basename(argv[0])+'-rc'
    os_name = get_os_name()
    level=os.popen('runlevel | awk {\'print $2\'}').readline()
    if os_name == 'RHEL' or os_name == 'CentOS':
        rc_init = os.path.join('/etc/rc.d/init.d/', rc_name)
        rc_link = os.path.join('/etc/rc.d/rc%s.d/' % (level.strip()), 'S99'+rc_name)
    elif os_name == 'Ubuntu' or os_name == 'Debian':
        rc_init = os.path.join('/etc/init.d/', rc_name)
        rc_link = os.path.join('/etc/rc%s.d/' % (level.strip()), 'S99'+rc_name)
    dir = os.path.dirname(os.path.abspath(argv[0]))
    if os.path.isfile(rc_init):
        os.remove(rc_init)
    if os.path.islink(rc_link):
        os.remove(rc_link)
    cmd = '%s %s' % (sys.executable, ' '.join(str(i) for i in argv))
    with open(rc_init, 'w') as f:
        f.write('''#!/bin/sh
#chkconfig: 35 99 99
#description: auto run
case "$1" in
    start)
        date >> /tmp/rc.tmp
        echo "start $0" | tee -a /tmp/rc.tmp
        sleep 10
        cd %s
        %s 2>&1 &
    ;;
    stop)
        date >> /tmp/rc.tmp
        echo "stop $0" | tee -a /tmp/rc.tmp
    ;;
    *)
        date >> /tmp/rc.tmp
        echo "$0: unknow command $1!" | tee -a /tmp/rc.tmp
        sleep 10
        cd %s
        %s 2>&1 &
    ;;
esac
exit 0''' % (dir,cmd,dir,cmd))
    os.system('sync')
    os.chown(rc_init, 0, 0)
    os.chmod(rc_init, stat.S_IRWXU + stat.S_IRGRP + stat.S_IROTH)
#    os.system('chkconfig --del %s' % (rc_init))
#    os.system('sleep 1')
#    os.system('chkconfig --level 35 %s on' % (rc_name))
    os.system('chown -R root %s' % rc_init)
    os.system('chmod +x %s' % rc_init)
    os.system('ln -s %s %s' % (rc_init, rc_link))
    print("Build rc at %s" % (rc_init))
    return

def linux_command_output_to_list(command):
    out_put_object = os.popen(command).readlines()
    out_put_list = [x.strip() for x in out_put_object]
    return out_put_list

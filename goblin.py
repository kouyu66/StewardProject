import socket
import time
import os
import uuid
import steward_lib


global running_scripts
running_scripts = []
# last_known_good = {}

def push(server, data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server, 6001))
    s.send((data).encode('utf-8'))  # 发送客户端有效数据
    # print(s.recv(1024).decode('utf-8')) # 接受服务器端的返回信息
    s.send(('').encode('utf-8'))    # 发送终止信息（空字符）
    s.close()   # 关闭连接
    return
# while True:

def get_host_info():

    current_info = []
    
    def get_disk_info():    # return nvme detail [dev, disk_status, dera_type, dera_info, dera_state]
        '''判断系统下nvme盘的个数，比对是否有对应的块设备，然后使用固定路径的nvme工具读取info以及state并存入字典，函数返回字典。'''
        nvme_detail = []    

        node_nvme_temp = os.popen("ls /dev/nvme* | grep -E '\/dev\/nvme.$'").readlines() # 包含\n的设备名 /dev/nvme0
        block_nvme_temp = os.popen("ls /dev/nvme* | grep -E \/dev\/nvme.n.$").readlines()   # 包含\n的块设备名 /dev/nvme0n1
        dera_info_list_temp = os.popen("/ge/auto/nvme dera info | grep '/'").readlines()    # 包含\n的dera info命令返回的信息列表，以

        node_nvme = [x.strip('\n') for x in node_nvme_temp] # 去掉'\n'
        block_nvme = [y.strip('\n') for y in block_nvme_temp]   # 去掉'\n'

        str_block_nvme = ';'.join(block_nvme)   # 将块设备信息转换为长字符串，便于检查node设备是否包含其中，来判断node设备对应的块设备被正确识别

        for dev in node_nvme:
            
            dera_info = ''
            dera_state = ''
            disk_status = ''
            
            if dev in str_block_nvme:   # 如果块设备字符串中包含字符设备，则表明块设备及字符设备均被识别
                disk_status = 0 # 字符设备及块设备均被识别，判断设备正常
            else:
                disk_status = 1 # 块设备未被识别，判断设备异常
            
            for info in dera_info_list_temp:
                
                if dev in info:
                    dera_info = ' '.join(info.split())   # 去除多余空格的nvme info信息
            
            pn_number = steward_lib.findString(dera_info, '\w{6}-\w{5}-\w{2}')[0] # 匹配SN号
            dera_type = steward_lib.mnToModule(pn_number)   # 将匹配的SN号转换为对应的卡类型

            dera_state_temp = os.popen("/ge/auto/nvme dera state {0}".format(dev)).readlines()
            dera_state = [' '.join(x.split()).strip('\n') for x in dera_state_temp] # 去除多余空格以及换行符以后的dera state状态信息列表
            single_disk_info = [dev, disk_status, dera_type, dera_info, dera_state]
            nvme_detail.append(single_disk_info)

        return nvme_detail
   
    def get_system_info():  # return system_info [mac, os_version, kernel_version, mainboard_info, cpu_info, mem_info, boot_drive_info]
        """获取 mainboard cpu mem maindisk ip mac os kernel 的信息"""
        
        def boot_drive_info():
            """首先获取/boot挂在点对应分区的UUID，然后查找该UUID对应的磁盘信息，判断是机械盘还是nvme盘，如果是机械盘，则调用smartctl命令读取磁盘信息，如果是nvme盘则使用nvme工具"""
            
            boot_drive_node_list = os.popen("cat /etc/fstab | grep 'UUID'| grep '/' | cut -d = -f 2 | cut -d ' ' -f 1 | xargs blkid -U").readlines() # xargs smartctl -a | grep -E "Device Model|Serial Number|Firmware Version|User Capacity"
            boot_drive_node = boot_drive_node_list[0].strip('\n')
        
            if '/dev/sd' in boot_drive_node:
                boot_drive_info = os.popen("smartctl -a {0} | grep -E 'Device Model|Serial Number|Firmware Version|User Capacity'".format(boot_drive_node)).readlines()
                # 需要调用smartctl工具， 软件包名为 smartmontools
                if len(boot_drive_info) <= 1:
                    boot_drive_info_readable = boot_drive_node # 如果没有安装smartctl，则返回node名称
                
            elif '/dev/nvme' in boot_drive_node:
                boot_drive_info = os.popen("/ge/auto/nvme dera info | grep {0}".format(boot_drive_node)).readlines()
            
            boot_drive_info_readable = [x.strip('\n') for x in boot_drive_info]
            
            return boot_drive_info_readable

        def os_version_info():
            """根据不同的linux操作系统获取version信息"""

            kernel = os.popen('uname -r').readlines()[0].strip('\n')
            
            os_distro = os.popen("cat /etc/os-release | grep 'ID'| grep -v 'VERSION_ID'|cut -d = -f 2").readlines()[0].strip('\n')
            
            if 'centos' in os_distro or 'redhat' in os_distro:
                os_ver = os.popen("cat /etc/redhat-release").readlines()[0].strip('\n')
            elif 'debian' in os_distro:
                os_sub_ver = os.popen("cat /etc/debian_version").readlines()[0].strip('\n')
                os_ver = 'debian {0}'.format(os_sub_ver)
            elif 'ubuntu' in os_distro:
                os_ver = os.popen("cat /etc/os-release | grep 'PRETTY_NAME'| cut -d \" -f 2")
            else:
                os_ver = 'null'
            return os_ver,kernel

        def cpu_info():

            cpu_list = os.popen("cat /proc/cpuinfo| grep 'model name' | cut -d : -f 2").readlines()
            cpu_core_num = len(cpu_list)
            cpu_name = cpu_list[0].strip('\n').strip()
            
            cpu_info = '{0} {1}'.format(cpu_name, cpu_core_num)

            return cpu_info
        
        def mem_info():
            
            current_mem_info = os.popen("free -h | grep 'Mem'").readlines()
            mem_total = [' '.join(x.split()).strip('\n') for x in current_mem_info][0].split()[1]
            
            return mem_total
        
        def mainboard_info():
            mainboard_manufacturer = os.popen("dmidecode -t baseboard | grep 'Manufacturer' | cut -d : -f 2").readlines()[0].strip('\n').strip()
            mainboard_type = os.popen("dmidecode -t baseboard | grep 'Product Name' | cut -d : -f 2").readlines()[0].strip('\n').strip()
            
            mac = uuid.UUID(int = uuid.getnode()).hex[-12:]
            mainboard = '{0} {1}'.format(mainboard_manufacturer, mainboard_type)
            return mac, mainboard
        
        def uptime_info():
            uptime_seconds = os.popen("cat /proc/uptime | cut -d ' ' -f 1").readlins()[0]
            m, s = divmod(uptime_seconds, 60)
            h, m = divmod(m, 60)
            uptime_readable = "%02d:%02d:%02d" % (h, m, s)
            
            return uptime_readable

        boot_drive_info = boot_drive_info()
        os_version, kernel_version = os_version_info()
        cpu_info = cpu_info()
        mem_info = mem_info()
        mac, mainboard_info = mainboard_info()
        uptime_info = uptime_info()
        
        system_info = [mac, os_version, kernel_version, mainboard_info, cpu_info, mem_info, boot_drive_info, uptime_info]
        
        return system_info

    def get_log_path(running_scripts): # ll /proc/pid | grep 'cwd' | cut -d ' ' -f 12



def checkRunningScript():
    """循环监控，每秒一次反馈当前测试机脚本运行状态，并获取脚本名及运行参数"""
    last_valid_process = {}
    while True:
        
        running_script_ps = os.popen("ps -elf | grep -v 'grep' | grep -E '\./ts_.* | \./runio.*'").readlines()  # check running script process
        uptime = float(os.popen("cat /proc/uptime | cut -d ' ' -f 1").readlines()[0])    # 获取系统已经启动了多久 秒数
        start_time = steward_lib.timeStamp()
        running_scripts = []    # 清空上次running script检查结果

        if not running_script_ps:
            pass
        else:
            # running_scripts = [steward_lib.findString(raw_script, '\./.*')[0].strip('\n') for raw_script in running_script_ps]  # 获取运行中脚本名以及参数          
            
            for raw_script in running_script_ps:    # 正对每条检测到的脚本进程执行操作
                
                pid = raw_script.split()[3] # 获取该进程的pid
                cwd = os.popen("ll /proc/{0} | grep 'cwd' | cut -d ' ' -f 12".format(pid)).readlines()[0]
                last_pid = last_valid_process.get(raw_script)
                
                if last_pid == pid: # 如果当前pid与上次pid一致，则将start_time置零
                    start_time = 0
                else:   # 如果pid与last_pid不一致或者last_pid不存在，则认为当前进程为新进程，更新start_time为当前时间戳
                    last_valid_process[raw_script] = pid
                    start_time = steward_lib.timeStamp()                    

                if 'pts' in raw_script:     # 通过进程开启用户为'pts' 判断该进程为用户手动开启的进程，
                    script_start_type = [0, start_time, cwd, steward_lib.findString(raw_script, '\./.*')[0].strip('\n')] # 0 表示手动启动的测试脚本                    
                else:
                    script_start_type = [1, start_time, cwd, steward_lib.findString(raw_script, '\./.*')[0].strip('\n')] # 1 表示自动启动的测试脚本

                running_scripts.append(script_start_type)
        sendInfo()        
        time.sleep(3)
def sendInfo():
    
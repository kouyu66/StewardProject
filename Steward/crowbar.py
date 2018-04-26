#!/usr/bin/env python3
#coding:utf-8
import os
import re
import time
import pickle
from collections import Counter

'''
ssd测试过程中用到的类信息
'''
# []

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
        self.counters = []  # [powerCycles, powerOnHours, unsafe_shutdowns, full_rebulid, raw_rebuild]
        self.err = [] # [pcie_uncorr_err, pcie_fatal_err, nand_init_fail, nand_erase_err, nand_program_err, media_err,init_pcie_vot_low_cnt, rt_pcie_vot_low_cnt]
    def load(self): 
        '''更新ssd状态信息'''
        # 获取pci速度信息
        get_pci_speed_cmd = "find /sys/* -name {0}|grep devices|cut -d '/' -f 6|xargs lspci -vvv -s|grep 'LnkSta:'|cut -d ' ' -f 2,4".format(self.diskname)
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
            self.counters = [powerCycles, powerOnHours, unsafe_shutdowns, full_rebulid, raw_rebuild]
            self.err = [pcie_uncorr_err, pcie_fatal_err, nand_init_fail, nand_erase_err, nand_program_err, media_err,init_pcie_vot_low_cnt, rt_pcie_vot_low_cnt]
        else:
            pass
        
        return


def get_running_script():   # 获取当前正在运行的脚本及参数，pid. 返回列表[[command1, args, pid]]
    '''获取当前正在运行的脚本及参数，pid. 返回列表[[command1, args, pid]]'''
    commands = []
    # 使用ps命令查看当前进程信息是否包含脚本名
    get_python3_script_fullname_cmd =  "ps -elf | grep -E 'HotPlug_NVMe_suite\.py|ts_.*\.py.*|runvdb.py.*'|grep -v grep"
    running_script_full_name = os.popen(get_python3_script_fullname_cmd).readlines()
    # 对返回的进程信息逐条进行拆分，拆分为命令本身和参数
    for cmd in running_script_full_name:
        # 使用正则表达式对进行信息进行拆分，以空格为分隔符
        cmd_tmp = re.split(' ', cmd)
        cmd_tmp = [x for x in cmd_tmp if x] # 去掉空字符
        for splited_cmd in cmd_tmp:
            command = []
            # 定位脚本名，及所在位置
            if '.py' in splited_cmd:
                pid = cmd_tmp[3]
                running_script_cmd = splited_cmd
                # 将脚本名后面的字符串作为参数，重新整合格式[command, args]
                running_script_args = ' '.join(cmd_tmp[cmd_tmp.index(splited_cmd)+1:]) # 截取脚本名后面的项，整合为空格分隔的字符串
                running_script_args = running_script_args.strip('\n')
                command = [running_script_cmd, running_script_args, pid]
                commands.append(command)
    return commands


def get_machine_status():   # 获取当前测试机信息，[厂商, 型号, cpu, 内存, nvme node, 开机时间, 网络状态]
    '''获取当前测试机信息，[厂商, 型号, cpu, 内存, nvme node, 开机时间, 网络状态]'''
    # 定义相关命令
    get_manufacturer_command = 'dmidecode -s system-manufacturer && dmidecode -s system-product-name'
    get_cpu_type_command = 'dmidecode -s processor-version'
    get_mem_count_command = 'dmidecode -t memory | grep Size: | grep -v No'
    get_men_type_command = "dmidecode -t memory | grep 'Type: DDR'|uniq"
    get_uptime_command = "cat /proc/uptime | cut -d ' ' -f 1"
    get_nvme_node_command = "ls /dev/nvme* | grep nvme.$"
    
    # 获取服务器厂商，型号信息
    machine_info = os.popen(get_manufacturer_command).readlines()
    machine_info = [x.strip('\n').strip() for x in machine_info]
    manufacturer, machine_type = machine_info
    # 获取服务器CPU信息
    cpu_info = os.popen(get_cpu_type_command).readlines()
    cpu_info = [x.strip('\n').strip() for x in cpu_info]
    cpus = ' '.join(['{0} * {1}'.format(str(x), str(y)) for x, y in Counter(cpu_info).items()])
    # 获取服务器内存信息
    mem_count = os.popen(get_mem_count_command).readlines()
    mem_count  = [x.strip('\n').strip() for x in mem_count]
    mem_type = os.popen(get_men_type_command).readlines()
    mem_type = [x.strip('\n').strip() for x in mem_type][0]
    mem_dict = Counter(mem_count)
    mems = ' '.join(['{0} * {1} {2}'.format(str(x), str(y), mem_type) for x, y in mem_dict.items()])
    # 获取dera nvme ssd字符设备信息
    node_info = os.popen(get_nvme_node_command).readlines()
    node_info = [x.strip('\n').strip() for x in node_info]
    for node in node_info:
        identify_info = os.popen("./nvme id-ctrl {0} | grep ^vid | cut -d ':' -f 2".format(node)).readlines()
        identify_info = [x.strip('\n').strip() for x in identify_info][0]
        if identify_info != '0x1d78':   # 排除非dera ssd
            node_info.remove(node)
    # 获取服务器开机时长信息
    uptime_seconds = os.popen(get_uptime_command).readlines()[0]
    uptime_seconds = float(uptime_seconds)
    m, s = divmod(uptime_seconds, 60)
    h, m = divmod(m, 60)
    uptime = "%02d:%02d:%02d" % (h, m, s)
    # 获取服务器当前网络状态信息
    local = '10.0.4.1' # 本地网关
    t_disk = '10.0.1.206' # T盘所在服务器的IP地址
    internet = 'www.baidu.com'  # 外网
    net_bucket = [local, t_disk, internet]
    net_status = ['1', '1', '1']
    for ip in net_bucket:
        ping_command = 'ping {0} -c 1 -w 1'.format(ip)
        respond = os.popen(ping_command).readlines()
        for line in respond:
            if 'ttl' in line:
                index = net_bucket.index(ip)
                net_status[index] = '0'
            else:
                pass
    net_status = ''.join(net_status)

    return [manufacturer, machine_type, cpus, mems, node_info, uptime, net_status]


def main():
    
    def timeStamp():
        now_time = datetime.datetime.now()
        readable_time = now_time.strftime('%Y-%m-%d_%H_%M_%S')
        return readable_time
    
    def list_compare(current_list, last_list):
        # 以第一个列表为基准，返回相对于第二个列表来说，增加的元素列表，和减少的元素列表
        item_add = []
        item_remove = []
        for current_item in current_list:
            if current_item not in last_list:
                item_add.append(current_item)
            else:
                last_list.remove(current_item)
        if last_list:
            item_remove = last_list
        return item_add, item_remove

    def genarate_current_trace(): # [nvme.names, nvme.vers, nvme.status, running_script, status]
        '''获取当前运行的脚本，机器状态，及ssd实例'''
        traces = []
        scripts = get_running_script()
        machine = get_machine_status()
        ssd = []
        for ssd_node in machine[4]:
            var_name = 'nvme%s'%str(machine[4].index(ssd_node))
            locals()[var_name] = SSD(ssd_node)
            ssd.append(locals()[var_name])
        # 以nvme ssd作为标的物，生成trace
        for nvme in ssd:
            nvme.load()
            node = nvme.node
            running_script = ''
            status = 'idle'
            
            if scripts:
                for script in scripts:
                    if 'ts_pwr.py' in script[0]:    # 由于ts_pwr和ts_top带有掉电测试，所以是全局式的脚本，所有ssd均受影响，所以只要有一个SSD在运行该测试，则认为所有ssd均受此影响
                        running_script = script
                        status = 'running'
                    elif 'ts_top.py' in script[0]:
                        running_script = script
                        status = 'running'
                    elif node in script[1]:
                        running_script = script
                        status = 'running'
                    else:
                        pass
            trace = [nvme.names, nvme.vers, nvme.status, running_script, status]
            traces.append(trace)
        return traces
    

    # -------- 以下为主要逻辑区域 --------
    
    def core_logic(current_trace, old_trace):
        # 首先判断两次检测卡的情况，是否有丢卡、重识别卡的情况

        current_card_info = [x[0] for x in current_trace if current_trace]  # 获取当前trace中ssd的names部分
        last_card_info = [x[0] for x in old_trace if old_trace] # 获取上次扫描中ssd的names部分
        add_card, remove_card = list_compare(current_card_info, last_card_info) # 判断是否有丢卡，或新识别卡的情况发生
        normal_card = [x for x in current_card_info if x not in add_card] # 既不是新添加的卡，也不包含弹出的卡
        machine = get_machine_status()  # 生成当前测试机状态

        if add_card:    # 处理新识别卡，这种情况
            
            def process_card_add(add_card):
                '''
                1.构建新trace，并通知Server端，归档旧trace，标志为'n(ew)'
                '''
                now_time = timeStamp()
                traces_tobe_send = ['N', now_time]
                archive = 'N'   # 该字段判断测试是否归档
                online = 'Y'    # 该字段判断SSD是否在线
                for card_name in add_card:
                    for trace in current_trace:
                        if card_name == trace[0]:
                            trace_tobe_send = [trace, machine, archive, online]
                            traces_tobe_send.append(trace_tobe_send)
                            
                return traces_tobe_send
            new_card = process_card_add(add_card)

        if remove_card:
            
            def process_card_remove(remove_card):
                '''
                1.构建新trace
                2.检查上次状态是否为idle
                3.如果上次为idle，则判断本次卡移除动作为正常弹出，报卡弹出给server端, 归档trace
                4.如果上次为running，则判断本次卡移出动作为丢卡，走丢卡流程， 归档trace
                '''
                now_time = timeStamp()
                traces_tobe_send = ['R', now_time]
                archive = 'Y'
                online = 'N'
                for card_name in remove_card:
                    for trace in old_trace:
                        if card_name == trace[0]:
                            if trace[3]:
                                trace[4] = 'Lost'
                            else:
                                trace[4] = 'Remove'
                            trace_tobe_send = [trace, machine, archive, online]
                            traces_tobe_send.append(trace_tobe_send)
                return traces_tobe_send
            remove_card = process_card_remove(remove_card)
        # 其次判断不存在丢卡及新添加卡的测试状态
        def process_normal_mode(normal_card):
            '''
            卡的数量与之前状态一致，则执行该流程
            1.检查脚本是否与之前一致
            2.如果一致，则发送heartbeat信号
            3.如果不一致，则记录状态变化，生成时间戳，发送给server端
            '''
            if not normal_card:
                return
            for card_name in normal_card:




    while True:
        
        current_trace = genarate_current_trace()
        old_trace = []
        if os.path.exists('last_scan.pickle'):
            with open('last_scan.pickle', 'rb') as last_scan:
                old_trace = pickle.load(last_scan)
        
        # 接下来是比对逻辑, 检查SSD信息变动


        
        
        # 将数据存储到本地文件
        # with open('last_scan.pickle', 'wb') as last_scan:
        #     pickle.dump(traces, last_scan)
        time.sleep(2)
main()

            # locals()['nvme%s'%machine[5].index(ssd_node)] = SSD(ssd_node)
            # ssd.append(locals()['nvme%s'%machine[5].index(ssd_node)])
            



#             uptime_seconds = os.popen("cat /proc/uptime | cut -d ' ' -f 1").readlins()[0]
#             m, s = divmod(uptime_seconds, 60)
#             h, m = divmod(m, 60)
#             uptime_readable = "%02d:%02d:%02d" % (h, m, s)
    # dmidecode -s system-manufacturer && dmidecode -s system-product-name
    # dmidecode -s processor-version
    # cat /proc/meminfo | grep MemTotal
    # dmidecode -t memory | grep 'Type: DDR'|uniq 
    # dmidecode -t memory | grep Size: | grep -v No
    # ping www.baidu.com -c 3 -w 1


# def get_host_info():

#     current_info = []
    
#     def get_disk_info():    # return nvme detail [dev, disk_status, dera_type, dera_info, dera_state]
#         '''判断系统下nvme盘的个数，比对是否有对应的块设备，然后使用固定路径的nvme工具读取info以及state并存入字典，函数返回字典。'''
#         nvme_detail = []    

#         node_nvme_temp = os.popen("ls /dev/nvme* | grep -E '\/dev\/nvme.$'").readlines() # 包含\n的设备名 /dev/nvme0
#         block_nvme_temp = os.popen("ls /dev/nvme* | grep -E \/dev\/nvme.n.$").readlines()   # 包含\n的块设备名 /dev/nvme0n1
#         dera_info_list_temp = os.popen("/ge/auto/nvme dera info | grep '/'").readlines()    # 包含\n的dera info命令返回的信息列表，以

#         node_nvme = [x.strip('\n') for x in node_nvme_temp] # 去掉'\n'
#         block_nvme = [y.strip('\n') for y in block_nvme_temp]   # 去掉'\n'

#         str_block_nvme = ';'.join(block_nvme)   # 将块设备信息转换为长字符串，便于检查node设备是否包含其中，来判断node设备对应的块设备被正确识别

#         for dev in node_nvme:
            
#             dera_info = ''
#             dera_state = ''
#             disk_status = ''
            
#             if dev in str_block_nvme:   # 如果块设备字符串中包含字符设备，则表明块设备及字符设备均被识别
#                 disk_status = 0 # 字符设备及块设备均被识别，判断设备正常
#             else:
#                 disk_status = 1 # 块设备未被识别，判断设备异常
            
#             for info in dera_info_list_temp:
                
#                 if dev in info:
#                     dera_info = ' '.join(info.split())   # 去除多余空格的nvme info信息
            
#             pn_number = steward_lib.findString(dera_info, '\w{6}-\w{5}-\w{2}')[0] # 匹配SN号
#             dera_type = steward_lib.mnToModule(pn_number)   # 将匹配的SN号转换为对应的卡类型

#             dera_state_temp = os.popen("/ge/auto/nvme dera state {0}".format(dev)).readlines()
#             dera_state = [' '.join(x.split()).strip('\n') for x in dera_state_temp] # 去除多余空格以及换行符以后的dera state状态信息列表
#             single_disk_info = [dev, disk_status, dera_type, dera_info, dera_state]
#             nvme_detail.append(single_disk_info)

#         return nvme_detail
   
#     def get_system_info():  # return system_info [mac, os_version, kernel_version, mainboard_info, cpu_info, mem_info, boot_drive_info]
#         """获取 mainboard cpu mem maindisk ip mac os kernel 的信息"""
        
#         def boot_drive_info():
#             """首先获取/boot挂在点对应分区的UUID，然后查找该UUID对应的磁盘信息，判断是机械盘还是nvme盘，如果是机械盘，则调用smartctl命令读取磁盘信息，如果是nvme盘则使用nvme工具"""
            
#             boot_drive_node_list = os.popen("cat /etc/fstab | grep 'UUID'| grep '/' | cut -d = -f 2 | cut -d ' ' -f 1 | xargs blkid -U").readlines() # xargs smartctl -a | grep -E "Device Model|Serial Number|Firmware Version|User Capacity"
#             boot_drive_node = boot_drive_node_list[0].strip('\n')
        
#             if '/dev/sd' in boot_drive_node:
#                 boot_drive_info = os.popen("smartctl -a {0} | grep -E 'Device Model|Serial Number|Firmware Version|User Capacity'".format(boot_drive_node)).readlines()
#                 # 需要调用smartctl工具， 软件包名为 smartmontools
#                 if len(boot_drive_info) <= 1:
#                     boot_drive_info_readable = boot_drive_node # 如果没有安装smartctl，则返回node名称
                
#             elif '/dev/nvme' in boot_drive_node:
#                 boot_drive_info = os.popen("/ge/auto/nvme dera info | grep {0}".format(boot_drive_node)).readlines()
            
#             boot_drive_info_readable = [x.strip('\n') for x in boot_drive_info]
            
#             return boot_drive_info_readable

#         def os_version_info():
#             """根据不同的linux操作系统获取version信息"""

#             kernel = os.popen('uname -r').readlines()[0].strip('\n')
            
#             os_distro = os.popen("cat /etc/os-release | grep 'ID'| grep -v 'VERSION_ID'|cut -d = -f 2").readlines()[0].strip('\n')
            
#             if 'centos' in os_distro or 'redhat' in os_distro:
#                 os_ver = os.popen("cat /etc/redhat-release").readlines()[0].strip('\n')
#             elif 'debian' in os_distro:
#                 os_sub_ver = os.popen("cat /etc/debian_version").readlines()[0].strip('\n')
#                 os_ver = 'debian {0}'.format(os_sub_ver)
#             elif 'ubuntu' in os_distro:
#                 os_ver = os.popen("cat /etc/os-release | grep 'PRETTY_NAME'| cut -d \" -f 2")
#             else:
#                 os_ver = 'null'
#             return os_ver,kernel

#         def cpu_info():

#             cpu_list = os.popen("cat /proc/cpuinfo| grep 'model name' | cut -d : -f 2").readlines()
#             cpu_core_num = len(cpu_list)
#             cpu_name = cpu_list[0].strip('\n').strip()
            
#             cpu_info = '{0} {1}'.format(cpu_name, cpu_core_num)

#             return cpu_info
        
#         def mem_info():
            
#             current_mem_info = os.popen("free -h | grep 'Mem'").readlines()
#             mem_total = [' '.join(x.split()).strip('\n') for x in current_mem_info][0].split()[1]
            
#             return mem_total
        
#         def mainboard_info():
#             mainboard_manufacturer = os.popen("dmidecode -t baseboard | grep 'Manufacturer' | cut -d : -f 2").readlines()[0].strip('\n').strip()
#             mainboard_type = os.popen("dmidecode -t baseboard | grep 'Product Name' | cut -d : -f 2").readlines()[0].strip('\n').strip()
            
#             mac = uuid.UUID(int = uuid.getnode()).hex[-12:]
#             mainboard = '{0} {1}'.format(mainboard_manufacturer, mainboard_type)
#             return mac, mainboard
        
#         def uptime_info():
#             uptime_seconds = os.popen("cat /proc/uptime | cut -d ' ' -f 1").readlins()[0]
#             m, s = divmod(uptime_seconds, 60)
#             h, m = divmod(m, 60)
#             uptime_readable = "%02d:%02d:%02d" % (h, m, s)
            
#             return uptime_readable

#         boot_drive_info = boot_drive_info()
#         os_version, kernel_version = os_version_info()
#         cpu_info = cpu_info()
#         mem_info = mem_info()
#         mac, mainboard_info = mainboard_info()
#         uptime_info = uptime_info()
        
#         system_info = [mac, os_version, kernel_version, mainboard_info, cpu_info, mem_info, boot_drive_info, uptime_info]
        
#         return system_info
    

# class Script():
#     def __init__(self):
#         self.scriptname = ''
#         self.scriptargs = ''
#         self.hours = 0
#         self.starttime = ''
#         self.estiend = ''
                
#     def load(self):
#         def get_script_name():
#             get_python3_script_fullname_cmd =  "ps -elf | grep -E 'ts.*\.py.*|runvdb.py.*'|grep -v grep"
#             running_script_full_name = os.popen(get_python3_script_fullname_cmd).readlines()
            

#         def get_script_args()
#         def get_script_time()
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
#!/usr/bin/env python3
#coding:utf-8
import json
import time
import datetime
import socket
import threading
import pandas as pd

def timeStamp():
    now_time = datetime.datetime.now()
    readable_time = now_time.strftime('%Y-%m-%d_%H_%M_%S')
    return readable_time

def dataRecv(sock, addr):
    '''循环等待客户端发出数据，如果发送空数据则断开链接，发送非空数据则交由 infomationExchange 函数处理'''
    # sock, addr = s.accept()
    # print('Accept new connetcion from {0}'.format(addr))
    # sock.send(b'Welcome!')
    while True:
        data = sock.recv(1024)
        if not data:
            break
        infomationExchange(data, addr)
    sock.close()
    # print('Connection from {0} closed.'.format(addr))

def infomationExchange(data, addr):
    """接受网络传输的 byte 类型数据，解码为 utf-8 并以首字符为识别码，判断数据请求类型，做出相应的数据处理。"""
     
    def dataIdentify(decode_data):
        if decode_data:
            info_type = decode_data.get('info_type')
        return info_type

    def processHeartBeat(decode_data):
        if not decode_data.get('info_type') == 'heartbeat':
            return
        timmer_pool[decode_data['SN']] = time.time()
        # info = '[Heart_Beat] {0} {1} online'.format(now_time, decode_data['SN'])
        # notes.append(info)
        return

    def processUpdate(decode_data):
        # 刷新计时器
        # 如果变动值属于关键属性（包含在new_trace当中），则除了打印log之外，还需要更改对应的关键值
        global main_info
        global timmer_pool
        
        if not decode_data.get('info_type') == 'normal_update':
            return      # 如果信息类型错误，说明信息有误，不作处理以免脚本报错
        decode_data.pop('info_type')
        
        line_number_list = main_info[(main_info.SN==decode_data['SN'])&(main_info.Archive=='no')].index.tolist()    # 定位统计表格中该trace的行号
        if line_number_list:                                                                                        # 定位统计表格中该trace的行号
            line_number = line_number_list[0]                                                                       # 定位统计表格中该trace的行号
        else:
            return      # 如果统计表格中不包含数据，则信息有误，不作处理
        
        sn = decode_data.pop('SN')
        test_machine_time = decode_data.pop('now_time')
        
        timmer_pool[sn] = time.time()    # 刷新计时器时间
        
        
        for key in decode_data.keys():  # 对所有变更信息做如下处理
            try:
                old_info, current_info = decode_data.get(key)   # 将变更数据解压到两个变量
                if key in main_info.columns:    # 判断关键信息是否出现变更
                # old_info = main_info.loc[line_number, key]                                                      # 如果关键信息变更，则读取统计表格中的旧数据
                    main_info.loc[line_number, key] = decode_data.get(key)[1]   # 将新数据写入统计表格                                          
                info = '[Update] {0} {1} {2} {3} {4} ==> {5}'.format(test_machine_time, addr[0], sn, key, old_info, current_info)  # 生成log信息
                notes.append(info)  
            except ValueError as e:
                print(addr[0], decode_data.get(key))

    def processCardRemove(decode_data):
        # 寻找trace的编号
        # online 设置为False
        # archive 设置为True
        info = ''
        if not decode_data.get('info_type') == 'card_remove':
            return
        # 找到本条trace对应的行号
        line_number_list = main_info[(main_info.SN==decode_data['SN'])&(main_info.Archive=='no')].index.tolist()
        if line_number_list:
            line_number = line_number_list[0]
            main_info.loc[line_number, 'Online'] = 'offline'
            main_info.loc[line_number, 'Archive'] = 'yes'
            if decode_data.get('err') == 1:
                main_info.loc[line_number, 'Err'] = 'yes'
        info = '[Eject] {0} {1} Card Eject Dected. SN: {2} Err: {3}.'.format(decode_data('now_time'), addr[0], decode_data('SN'), decode_data.get('err'))
        notes.append(info)
        return 

    def processNewTrace(decode_data):
        
        if not decode_data.get('info_type') == 'new_trace':
            return
        
        global main_info
        global now_time

        decode_data['IP'] = addr[0]
        decode_data['Online'] = 'online'
        decode_data['Archive'] = 'no'
        decode_data['Err'] = 'no'
        timmer_pool[decode_data['SN']] = time.time()    # 将当前时间以sn为键值，记录到全局字典中
        decode_data.pop('info_type')
       
        # 归档旧数据
        if not main_info.empty:
            line_number_list = main_info[(main_info.SN==decode_data['SN'])&(main_info.Archive=='no')].index.tolist()
            if line_number_list:
                line_number = line_number_list[0]
                main_info.loc[line_number, 'Archive'] = 'yes'
        
        # 添加新数据
        main_info = main_info.append(decode_data, ignore_index=True)
        info = '[New_Trace] {0} {1} {2}'.format(now_time, addr[0], decode_data['SN'])
        notes.append(info)
        return

    def dataProcess(info_type):
        if info_type == 'heartbeat':
            processHeartBeat(decode_data)  # 处理heartbeat的函数
        elif info_type == 'normal_update':
            processUpdate(decode_data)     # 处理update消息的函数
        elif info_type == 'new_trace':
            processNewTrace(decode_data)   # 处理newtrace的函数
        elif info_type == 'card_remove':
            processCardRemove(decode_data) # 处理丢卡的函数

        return
    
    decode_data = json.loads(data.decode('utf-8'))  # 解压原始数据
    notes = []  # 清空log信息
    info_type = dataIdentify(decode_data)   # 识别信息类型
    dataProcess(info_type)  # 处理对应类型的信息
    with open('trace.txt', 'a') as log: # 写log
        for line in notes:
            log.write(line + '\n')
        log.close() 
    return

def out_put(main_info, frequent=60):
    # while True:
    if not main_info.empty:
        main_info.to_excel('Total_info.xlsx')
        # time.sleep(60)
    return

def timmer(timmer_pool):
    # while True:
    timmer_sn = timmer_pool.copy()
    for sn in timmer_sn.keys():
        if time.time() - timmer_sn.get(sn) > 1200: # 该sn超过1200s(20分钟)无响应
            line_number_list = main_info[(main_info.SN==sn)&(main_info.Archive=='no')].index.tolist()
            if line_number_list:
                line_number = line_number_list[0]
                main_info.loc[line_number, 'Online'] = 'offline'
        # time.sleep(5)
    return

# -------- main --------#
global now_time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 6001))
s.listen(5)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)   # 在服务器端不使用该端口号时，释放资源

now_time = timeStamp()
main_info = pd.DataFrame(columns=['IP','machine', 'boot', 'pcispeed', 'device_status', 'SN', 'Model', 'Capacity', 'Format', 'FwRev', 'Err', 'fw_loader_version', 'uefi_driver_version', 'script', 'Online', 'Archive'])
timmer_pool = {}    # 创建包含 sn : heart_beat_local_time的本地字典，用来统计ssd的心跳时间

while True:
    sock, addr = s.accept()
    t1 = threading.Thread(target=dataRecv, args=(sock, addr))
    t1.start()
    timmer(timmer_pool)
    out_put(main_info)

    
    

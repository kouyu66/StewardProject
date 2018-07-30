#!/usr/bin/env python3
# coding:utf-8

import os
import json
import time
import datetime
import socket
import threading
import pandas as pd

global now_time
global timmer_pool
global main_info
global notes


# 获取时间戳函数：
def timeStamp():
    now_time = datetime.datetime.now()
    readable_time = now_time.strftime('%Y-%m-%d %H:%M:%S') + ' [MC]'

    return readable_time


# 计时器函数：
def timmer(timmer_pool):
    # while True:
    timmer_sn = timmer_pool.copy()
    for sn in timmer_sn.keys():
        line_number_list = main_info[
            (main_info.SN == sn) & (main_info.Archive == 'no')].index.tolist()
        if line_number_list:
            line_number = line_number_list[0]
            
            dif = time.time() - timmer_sn.get(sn)

            if dif > 8:
                main_info.loc[line_number, 'Online'] = 'L.O.S [{0}s]'.format(dif)
            else:
                main_info.loc[line_number, 'Online'] = 'Online'
        else:
            info = 'timmer check error,{1} in timmer list but not in main_info {0}'.format(
                addr[0], sn)
            print(info)
    del timmer_sn

    return


# 输出excel函数：
def out_put(main_info, frequent=60):
    # while True:
    if not main_info.empty:
        main_info.to_excel('Total_info.xlsx')
        # time.sleep(60)
    return


# 接收消息函数：
def dataRecv(sock, addr):
    '''循环等待客户端发出数据，如果发送空数据则断开链接，发送非空数据则交由 infomationExchange 函数处理'''
    # sock, addr = s.accept()
    # print('Accept new connetcion from {0}'.format(addr))
    # sock.send(b'Welcome!')
    while True:
        data = sock.recv(1024)
        if not data:
            break
        infomationExchange(sock, data, addr)
    sock.close()
    # print('Connection from {0} closed.'.format(addr))
    return


# ------ 创建socket服务器 ------#
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 6001))
s.listen(5)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 在服务器端不使用该端口号时，释放资源


# 信息处理函数：
def infomationExchange(sock, data, addr):
    """接受网络传输的 byte 类型数据，解码为 utf-8 并以首字符为识别码，判断数据请求类型，做出相应的数据处理。"""

    def dataIdentify(decode_data):  # 识别传入信息的类型
        info_type = decode_data.get('info_type')
        return info_type

    def dataProcess(info_type):  # 将传入信息交由特定函数处理

        if info_type == 'heartbeat':
            processHeartBeat(decode_data)  # 处理heartbeat的函数
        elif info_type == 'normal_update':
            processUpdate(decode_data)  # 处理update消息的函数
        elif info_type == 'new_trace':
            processNewTrace(decode_data)  # 处理newtrace的函数
        elif info_type == 'card_remove':
            processCardRemove(decode_data)  # 处理丢卡的函数
        elif info_type == 'fetch':
            processClientFetch(decode_data)
        return

    def processHeartBeat(decode_data):  # 处理heratbear
        global timmer_pool

        timmer_pool[decode_data['SN']] = time.time()  # 刷新计时器时间为当前时间
        return

    def processUpdate(decode_data):  # 处理update信息

        global main_info
        global timmer_pool
        global notes

        decode_data.pop('info_type')

        # ------ 判断统计表是否追踪该trace消息 ------#
        line_number_list = main_info[(main_info.SN == decode_data['SN']) & (
            main_info.Archive == 'no')].index.tolist()  # 定位统计表格中该trace的行号
        if line_number_list:  # 定位统计表格中该trace的行号
            line_number = line_number_list[0]  # 定位统计表格中该trace的行号
        else:
            print('update process failed. no matched trace found.{0} - {1}'.
                  format(addr[0], decode_data['SN']))
            return

        # ------ 刷新计时器时间 ------ #
        sn = decode_data.pop('SN')
        test_machine_time = decode_data.pop(
            'now_time')  # 为了便于核对错误信息，此处时间使用client端时间
        timmer_pool[sn] = time.time()  # 刷新计时器时间

        # ------ 判断关键信息是否变更 ------ #
        for key in decode_data.keys():  # 对所有变更信息做如下处理
            global notes

            try:
                old_info, current_info = decode_data.get(key)  # 将变更数据解压到两个变量
                if key in main_info.columns:  # 判断关键信息是否出现变更
                    # old_info = main_info.loc[line_number, key]
                    main_info.loc[line_number, key] = decode_data.get(key)[1]
        # ------ 生成log信息 ------ #
                info = '[Update] {0} {1} {2} {3} {4} ==> {5}'.format(
                    test_machine_time, addr[0], sn, key, old_info,
                    current_info)  # 生成log信息

                with open(sn, 'a') as log:
                    log.write(info + '\n')

                notes.append(info)
            except ValueError as e:
                print('ValueErr, old_info, current_info required.')
                print(addr[0], decode_data.get(key))
        return

    def processCardRemove(decode_data):
        # 寻找trace的编号
        # online 设置为False
        # archive 设置为True

        global timmer_pool
        global notes
        info = ''

        # 删除该ssd对应的计时器
        timmer_pool.pop(decode_data['SN'])

        # 找到本条trace对应的行号
        line_number_list = main_info[(main_info.SN == decode_data['SN']) & (
            main_info.Archive == 'no')].index.tolist()
        if line_number_list:
            line_number = line_number_list[0]

            # 将offline信息及归档信息刷新到表格：
            main_info.loc[line_number, 'Online'] = 'Offline'
            main_info.loc[line_number, 'Archive'] = 'yes'

            # 判断ssd是否异常退出：
            if decode_data.get('err') == 1:
                main_info.loc[line_number, 'Err'] = 'yes'

        # 发送trace信息到日志
        info = '[Eject] {0} {1} Card Eject Dected. SN: {2} Err: {3}.'.format(
            decode_data['now_time'], addr[0], decode_data['SN'],
            decode_data.get('err'))

        with open(decode_data['SN'], 'a') as log:
            log.write(info + '\n')

        notes.append(info)
        return

    def processNewTrace(decode_data):

        global main_info
        global now_time
        global notes

        decode_data['IP'] = addr[0]
        decode_data['Online'] = 'Online'
        decode_data['Archive'] = 'no'
        decode_data['Err'] = 'no'
        timmer_pool[decode_data['SN']] = time.time()  # 将当前时间以sn为键值，记录到全局字典中
        decode_data.pop('info_type')

        # 归档旧数据
        if not main_info.empty:
            line_number_list = main_info[
                (main_info.SN == decode_data['SN'])
                & (main_info.Archive == 'no')].index.tolist()
            if line_number_list:
                line_number = line_number_list[0]
                main_info.loc[line_number, 'Archive'] = 'yes'

        # 添加新数据
        main_info = main_info.append(decode_data, ignore_index=True)
        info = '[New_Trace] {0} {1} {2}'.format(now_time, addr[0],
                                                decode_data['SN'])
        with open(decode_data['SN'], 'a') as log:
            log.write(info + '\n')
        notes.append(info)
        return

    def processClientFetch(decode_data):
        '''处理main_info，将数据处理为嵌套列表进行发送'''
        global main_info

        value_in_box = main_info.values.tolist()
        list_value = []

        for value in value_in_box:
            if value[0] == 'yes':  # 归档数据在GUI界面不显示
                continue

            matchedValue = value[1:]  # 不显示归档信息
            list_value.append(matchedValue)

        value_in_box_dump = json.dumps(list_value).encode('utf-8')

        info_length = str(len(value_in_box_dump))
        sock.send(info_length.encode('utf-8'))  # 通知客户端本次的发送量
        sock.send(value_in_box_dump)
        #        sock.close()
        return

    global notes

    decode_data = json.loads(data.decode('utf-8'))  # 解压原始数据
    notes = []  # 清空log信息
    info_type = dataIdentify(decode_data)  # 识别信息类型
    dataProcess(info_type)  # 处理对应类型的信息

    with open('trace.txt', 'a') as log:  # 写log
        for line in notes:
            log.write(line + '\n')

    return


# ------ 创建基础数据结构 ------ #
timmer_pool = {}  # 创建包含 sn : heart_beat_local_time的本地字典，用来统计ssd的心跳时间

if os.path.exists('Total_info.xlsx'):
    main_info = pd.read_excel('Total_info.xlsx')
else:
    main_info = pd.DataFrame(columns=[
    'Archive', 'IP', 'SN', 'boot', 'Online', 'device_status', 'pcispeed',
    'script', 'start_time', 'stop_time', 'Err', 'Model', 'Capacity', 'FwRev',
    'Format', 'fw_loader_version', 'uefi_driver_version', 'machine'
])

# ------创建主循环结构 ------#
while True:
    now_time = timeStamp()
    sock, addr = s.accept()
    t1 = threading.Thread(target=dataRecv, args=(sock, addr))
    t1.start()
    timmer(timmer_pool)
    out_put(main_info)

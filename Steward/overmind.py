#!/usr/bin/env python3
#coding:utf-8
import json
import socket
import threading
import pandas as pd


def dataRecv(sock, addr):
    '''循环等待客户端发出数据，如果发送空数据则断开链接，发送非空数据则交由 infomationExchange 函数处理'''
    # sock, addr = s.accept()
    print('Accept new connetcion from {0}'.format(addr))
    # sock.send(b'Welcome!')
    while True:
        data = sock.recv(1024)
        if not data:
            break
        infomationExchange(data, addr)
    sock.close()
    print('Connection from {0} closed.'.format(addr))

def infomationExchange(data, addr):
    """接受网络传输的 byte 类型数据，解码为 utf-8 并以首字符为识别码，判断数据请求类型，做出相应的数据处理。"""
     
    decode_data = json.loads(data.decode('utf-8'))
    
    def dataIdentify(decode_data):
        if decode_data:
            info_type = decode_data.get('info_type')
        return info_type

    def processHeartBeat(decode_data):
        if not decode_data.get('info_type') == 'heartbeat':
            return
        current_beat_time = 


    def processUpdate(decode_data):
        # 刷新计时器
        # 如果变动值属于关键属性（包含在new_trace当中），则除了打印log之外，还需要更改对应的关键值
        
        if not decode_data.get('info_type') == 'normal_update':
            return
        line_number_list = main_info[(main_info.SN==decode_data['SN'])&(main_info.Archive=='no')].index.tolist()
        if line_number_list:
            line_number = line_number_list[0]
            for key in decode_data.keys():
                if key in main_info.columns:
                    old_info = main_info.loc[line_number, key]
                    main_info.loc[line_number, key] = decode_data.get(key)
                info = '{0} {1} {2} {3} {4} ==> {5}'.format(decode_data.get('now_time'), addr, decode_data.get('SN'), key, old_info, decode_data.get(key))

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
        info = '{0} {1} Card Eject Dected. SN:{2}.\n'.format(decode_data('now_time'), addr, decode_data('SN'))

        return 

    def processNewTrace(decode_data):
        
        if not decode_data.get('info_type') == 'new_trace':
            return
        decode_data['IP'] = addr
        decode_data['Online'] = 'online'
        decode_data['Archive'] = 'no'
        decode_data['Err'] = 'no'
        # 归档旧数据
        line_number_list = main_info[(main_info.SN==decode_data['SN'])&(main_info.Archive=='no')].index.tolist()
        if line_number_list:
            line_number = line_number_list[0]
            main_info.loc[line_number, 'Archive'] = 'yes'
        # 添加新数据
        main_info = main_info.append(decode_data, ignore_index=True)
        info = '{0}'
        return
'

        # 构建新trace



        # 添加两列数据: online 和 archive 分别用来标示ssd是否在线，和当前记录是否有效
        # 将数据写到pandas
        # 对该trace进行编号
        # 对该trace设置一个计时器，用来监控heartbeat


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
    

    dataIdentify(data)

    return


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 6001))
s.listen(5)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)   # 在服务器端不使用该端口号时，释放资源

# 创建一个data_frame格式如下：
# machine boot pcispeed device_status sn mn cap format fw fwld uefi script online archive 
main_info = pd.DataFrame(columns=['IP','machine', 'boot', 'pcispeed', 'device_status', 'SN', 'MN', 'Capacity', 'Fromat', 'FwRev', 'Err', 'fw_loader_version', 'uefi_driver_version', 'script', 'Online', 'Archive'])


while True:
    sock, addr = s.accept()
    t = threading.Thread(target=dataRecv, args=(sock, addr))
    t.start()
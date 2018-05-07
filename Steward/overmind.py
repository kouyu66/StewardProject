#!/usr/bin/env python3
#coding:utf-8
import json
import socket
import threading
import pandas

def dataRecv(sock, addr):
    '''循环等待客户端发出数据，如果发送空数据则断开链接，发送非空数据则交由 infomationExchange 函数处理'''
    # sock, addr = s.accept()
    print('Accept new connetcion from {0}'.format(addr))
    # sock.send(b'Welcome!')
    while True:
        data = sock.recv(1024)
        if not data:
            break
        infomationExchange(data)
    sock.close()
    print('Connection from {0} closed.'.format(addr))

def infomationExchange(data):
    """接受网络传输的 byte 类型数据，解码为 utf-8 并以首字符为识别码，判断数据请求类型，做出相应的数据处理。"""
     
    decode_data = json.loads(data.decode('utf-8'))
    
    def dataIdentify(decode_data):
        if decode_data:
            info_type = decode_data.get('info_type')
        return info_type

    def processHeratBeat(decode_data):
        # 刷新计时器 

    def processUpdate(decode_data):
        # 刷新计时器

    def processCardRemove(decode_data):
        # 寻找trace的编号
        # onlie 设置为False
        # archive 设置为True

    def processNewTrace(decode_data):
        # 将数据写到pandas
        # 对该trace进行编号
        # 对该trace设置一个计时器，用来监控heartbeat


    def dataProcess(info_type):
        if info_type == 'heartbeat':
            processHeratBeat(decode_data)  # 处理heartbeat的函数
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


while True:
    sock, addr = s.accept()
    t = threading.Thread(target=dataRecv, args=(sock, addr))
    t.start()
#!/usr/bin/env python3
#coding:utf-8
import json
import socket
import threading

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
     
    def dataIdentify(data):
        decode_data = json.loads(data.decode('utf-8'))
        print(decode_data)
        return
    dataIdentify(data)

    return


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 6001))
s.listen(5)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)   # 在服务器端不使用该端口号时，释放资源



while True:
    sock, addr = s.accept()
    t = threading.Thread(target=dataRecv, args=(sock, addr))
    t.start()
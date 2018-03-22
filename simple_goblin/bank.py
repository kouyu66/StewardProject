import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 6001))
s.listen(5)

current_info = {}


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
    def info_diff(list1,list2):
        list1_diff = []
        list2_diff = []
        for item1 in list1:
            for item2 in list2:
                if item1 != item2:
                    list1_diff.append(item1)
                    list2_diff.append(item2)
        return list1_diff, list2_diff


    def dataIdentify(data):
        decode_data = data.decode('utf-8').split()
        opcode, sys_info, card_info, script_info = decode_data  # 将收到的信息解包到各个变量
        if opcode == 'g0':

            
            return

        # elif opcode == 'g1':    # 发送测试信息发生变动时
        #     print('bank recv g1')
        # elif opcode == 'g2':
        #     print('bank recv g2')
        # elif opcode == 'g3':
        #     print('bank recv g3')
        # return
    dataIdentify(data)
    return
while True:
    sock, addr = s.accept()
    t = threading.Thread(target=dataRecv, args=(sock, addr))
    t.start()

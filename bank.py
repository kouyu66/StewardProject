import socket
import threading

# global last_known_good_running
# # global script_start_running

# last_known_good_running = {}
# script_start_running = {}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 6001))
s.listen(5)
s.setsockopt(socket.SOL_SOCYET,socket.SO_REUSEADDR,1)

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
        decode_data = data.decode('utf-8').split()
        opcode = decode_data[0]

        if opcode == 'HB':  # 常量数据与上次检测一致，则客户端仅发送HeartBeat消息
            print(decode_data)
            return

        elif opcode == 'Err':   # 检测到错误信息，则发送
            print('bank recv g1')
        elif opcode == 'g2':
            print('bank recv g2')
        elif opcode == 'g3':
            print('bank recv g3')
        return
    dataIdentify(data)
    # dataAnalyze()
    # dataFlow()
    # serverRespond()
    return
while True:
    sock, addr = s.accept()
    t = threading.Thread(target=dataRecv, args=(sock, addr))
    t.start()

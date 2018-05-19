#!/usr/bin/env python3
# chkconfig:2345 80 90
# description:crowbar.py
# coding:utf-8

import os
import json
import socket
import pandas as pd
import tkinter
from tkinter.ttk import Treeview

global main_info


def request(command, server_ip='10.0.4.155'):
    result = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server_ip, 6001))

        s.send((command).encode('utf-8'))  # 发送请求
        total_size = s.recv(1024).decode('utf-8')  # 获取待接收字符的长度
        size = 0
        result = ''

        while size < int(total_size):  # 处理数据分多个数据包发送的情况
            res = s.recv(1024).decode('utf-8')
            result += res
            size += len(res)

        s.send(('').encode('utf-8'))  # 发送终止信息（空字符）
#        s.close()  # 关闭连接
    except ConnectionRefusedError as e:
        print('overmind offline.')

    return result


def process_result(result):
    global main_info

    db = json.loads(result)
    main_info = pd.DataFrame(db)
    value_in_box = main_info.values.tolist()

    list_value = []
    for value in value_in_box:
        if value[0] == 'yes':   # 归档数据在GUI界面不显示
            continue
        matchedValue = [
            value[5], value[8], value[9], value[7], value[10],
            value[13], value[14], value[15], value[16], value[2], value[6],
            value[1], value[4], value[3], value[11], value[17], value[12]
        ]
        list_value.append(matchedValue)

    return list_value


def fetchAndDisplay():
    cmd = {'info_type': 'fetch'}
    command = json.dumps(cmd)
    main_info_str = request(command)
    screen_list = process_result(main_info_str)
    
    last_screen = monitordisplay.get_children() # 清空上一屏
    for item in last_screen:
        monitordisplay.delete(item)
        
    for line in screen_list:    # 写入当前数据
        monitordisplay.insert('', 'end', values=line)
    
    return


def dump_to_excel():
    global main_info
    if main_info.empty:
        print('no main_info found.')
        return
    main_info.to_excel('Total_Info.xlsx')
    return


def copy_ssd_history():
    iids = monitordisplay.selection()
    t = iids[0]
    sn = monitordisplay.item(t, 'values')[1]
    os.system('pscp -q -pw Password1 root@10.0.4.155:/control/{0} .'.format(sn))
    
    return
    
    

root = tkinter.Tk()
label = tkinter.Label(root, text='Dera System Test Monitor')
label.pack()
button1 = tkinter.Button(root, text='Dump To Excel', command=dump_to_excel)
button1.pack(side=tkinter.TOP, anchor='w')
button2 = tkinter.Button(root, text='Refresh', command=fetchAndDisplay)
button2.pack(side=tkinter.BOTTOM, anchor='e')
button3 = tkinter.Button(root, text='Dump Selected Item History', command=copy_ssd_history)
button3.pack(side=tkinter.BOTTOM, anchor='s')
monitorfm = tkinter.Frame(root)
monitorsb = tkinter.Scrollbar(monitorfm)
monitorsb.pack(side=tkinter.RIGHT, fill=tkinter.Y)
monitordisplay = Treeview(
    root,
    columns=('C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10',
             'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18'),
    show='headings',
    yscrollcommand=monitorsb.set)
# monitordisplay.column('C1', width=50, anchor='center')
# monitordisplay.heading('C1', text='Archive')
monitordisplay.column('C1', width=70, anchor='center')
monitordisplay.heading('C1', text='IP')
monitordisplay.column('C2', width=110, anchor='center')
monitordisplay.heading('C2', text='SN')
monitordisplay.column('C3', width=50, anchor='center')
monitordisplay.heading('C3', text='Boot')
monitordisplay.column('C4', width=80, anchor='center')
monitordisplay.heading('C4', text='Online')
monitordisplay.column('C5', width=60, anchor='center')
monitordisplay.heading('C5', text='Status')
monitordisplay.column('C6', width=60, anchor='center')
monitordisplay.heading('C6', text='Speed')
monitordisplay.column('C7', width=110, anchor='center')
monitordisplay.heading('C7', text='Script')
monitordisplay.column('C8', width=70, anchor='center')
monitordisplay.heading('C8', text='Start')
monitordisplay.column('C9', width=70, anchor='center')
monitordisplay.heading('C9', text='Stop')
monitordisplay.column('C10', width=50, anchor='center')
monitordisplay.heading('C10', text='Error')
monitordisplay.column('C11', width=100, anchor='center')
monitordisplay.heading('C11', text='Model')
monitordisplay.column('C12', width=50, anchor='center')
monitordisplay.heading('C12', text='Cap')
monitordisplay.column('C13', width=60, anchor='center')
monitordisplay.heading('C13', text='Firmware')
monitordisplay.column('C14', width=50, anchor='center')
monitordisplay.heading('C14', text='Format')
monitordisplay.column('C15', width=60, anchor='center')
monitordisplay.heading('C15', text='Fwld')
monitordisplay.column('C16', width=60, anchor='center')
monitordisplay.heading('C16', text='UEFI')
monitordisplay.column('C17', width=200, anchor='center')
monitordisplay.heading('C17', text='Machine')
# monitordisplay.bind()
monitorsb.config(command=monitordisplay.yview)
monitordisplay.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
monitorfm.pack()


# ------ Under Construction ------ #
fetchAndDisplay()

root.mainloop()

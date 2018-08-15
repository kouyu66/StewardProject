'''本单元测试用于将linux文本行输出数据进行处理，使用matlab函数绘制折线图'''
import os
import re
import time
import csv
import pandas as pd
import matplotlib.pyplot as plt

# 注意，双引号是命令的一部分
command_list = ['"#419b 0 0"', '"#519b 0 0"', '"#b19b 0 0"', '"#c19b 0 0"'] 
dev = '/dev/nvme0'
temp_set = '55_-10'


def get_mgcErr(command_list):
    mgc1 = []
    mgc2 = []
    mgc3 = []
    mgc4 = []
    numbers = []
    
    for cmd in command_list:
        get_error_info_cmd = "./nvme dera uart-in -p {0} {1}".format(cmd, dev) 
        cpu_info = os.popen(get_error_info_cmd).readlines()
        # 检查返回值是否正常
        if not cpu_info:
            print('check fw version.')
            return
        time.sleep(1)
        # 返回值正常的前提下，获取mgc error info信息
        mgc_info = os.popen("./nvme dera get-log {0} | grep -E 'ERRBit|ERRUNC'|cut -d ' ' -f 4".format(dev)).readlines()
        # 对mgc error info信息逐行提取目标数字，生成一个嵌套列表
        for line in mgc_info:
            number = re.findall(r">?\d+", line)
            numbers.append(number)
        # 把生成的errbit信息赋值给对应的mgc
        if '0x8' in cpu_info[0]:
            mgc1 = numbers
            numbers = []
        elif '0x10' in cpu_info[0]:
            mgc2 = numbers
            numbers = []
        elif '0x200' in cpu_info[0]:
            mgc3 = numbers
            numbers = []
        elif '0x400' in cpu_info[0]:
            mgc4 = numbers
            numbers = []
    return mgc1, mgc2, mgc3, mgc4


def list_to_csv(list_name, csv_name, headline):
    # headline 为csv的标题行
    with open(csv_name, 'w', newline='') as csv_obj:
        writer = csv.writer(csv_obj)
        writer.writerow(headline)
        data = list_name
        writer.writerows(data)
        csv_obj.close()
    return


def csv_to_jpg(csv_filename_list, jpg_filename):
    # 调用pandas模块处理csv文件，首先将csv文件导入为pandas的dataframe（一种类似sheet页的数据格式）
    # plt.grid(True)
    # 构图元素赋值 
    x = list(range(0, 74))
    y_list = []
    for csv_filename in csv_filename_list:
        df = pd.read_csv(csv_filename)
        y = df['FrameCnt']
        y_list.append(y)
    labels = ['-20,55', '-10,55', '0,55', '10,55', '10,10', '55,-10', '55,0', '55,10', '55,-20', '0,0', '-10,-10', '-20,-20', '55,55', '25,25']
    colors = ['black', 'silver', 'red', 'orange', 'yellow', 'lime', 'blue', 'purple', 'pink', 'slategray', 'aqua', 'sienna', 'lightsteelblue', 'fuchsia']
    plt.figure(figsize=(8, 6), dpi=80)
    
    # 全图
    plt.subplot(211)
    plt.grid(True)
    plt.xticks(x)
    plt.xlabel('ErrBit')
    plt.ylabel('Frame Count')
    x0 = x
    colors0 = colors[:]
    for y in y_list:
        plt.plot(x, y, linewidth=2.0, color=colors0.pop(0))
    plt.legend(labels)
    # 前30 ErrBit的图
    plt.subplot(223)
    plt.grid(True)
    plt.xticks(x)
    plt.xlabel('ErrBit')
    plt.ylabel('Frame Count')
    x1 = x[:30]
    colors1 = colors[:]
    for y in y_list:
        y1 = y[:30]
        plt.plot(x1, y1, linewidth=2.0, color=colors1.pop(0))

    # 后10 ErrBit的图
    plt.subplot(224)
    
    plt.grid(True)
    plt.xticks(x)
    plt.xlabel('ErrBit')
    plt.ylabel('Frame Count')
    colors2 = colors[:]
    x2 = x0[-14:]
    for y in y_list:
        y2 = y[-14:]
        plt.plot(x2, y2, linewidth=2.0, color=colors2.pop(0))
    
    plt.savefig('mgc1.png')
    return


csv_filename_list = ['m2055.csv', 'm1055.csv', '055.csv', '1055.csv', '1010.csv', '55m10.csv', '550.csv', '5510.csv', '55m20.csv', '00.csv', 'm10m10.csv', 'm20m20.csv', '5555.csv', '2525.csv']
csv_to_jpg(csv_filename_list, '55_-10_mgc1.jpg')
# mgc1, mgc2, mgc3, mgc4 = get_mgcErr(command_list)
# mgc_info = [mgc1, mgc2, mgc3, mgc4]
# for mgc in mgc_info:
#     csv_name = temp_set + '_mgc' + str(mgc_info.index(mgc) + 1)
#     list_to_csv(mgc, csv_name, ['ErrBit', 'FrameCnt', 'Rate'])

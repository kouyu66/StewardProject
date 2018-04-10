#!/usr/bin/env python3
# -*- Coding: UTF-8 -*-
import os
import csv
import time
import datetime
import re
from random import choice

def main():

    def temp_sets(high_temps=[55],low_temps=[-20,-10,0,10],rt=[25],mode='mix'): # 根据参数生成需要测试的温度组合
        mix_temp = []
        mix_temp.extend(high_temps)
        mix_temp.extend(low_temps)
        mix_temp.extend(rt)

        basic_set = [[x,x] for x in mix_temp]   # 
        high_low_set = [[x,y] for x in high_temps for y in low_temps]
        low_high_set = [[x,y] for x in low_temps for y in high_temps]

        all_sets = []
        
        if mode is 'mix':   # 混合测试包含 高-低，低-高，高-高, 低-低 常温-常温
            all_sets.extend(basic_set)
            all_sets.extend(high_low_set)
            all_sets.extend(low_high_set)
        elif mode is 'h':   # 仅包含 高-低
            all_sets.extend(high_low_set)
        elif mode is 'l':   # 仅包含 低-高
            all_sets.extend(low_high_set)
        elif mode is 'hl':  # 仅包含 高-低，低-高
            all_sets.extend(high_low_set)
            all_sets.extend(low_high_set)
        
        print('Temp set going to run: {0}'.format(all_sets))
        
        return all_sets

    def get_sensor_temp(nvme_dev="/dev/nvme0"):   # 获取SSD温度传感器温度列表

        if not os.path.exists('nvme'):  # 获取nvme工具
            os.popen('cp /system_repo/tools/nvme/nvme .')
        
        get_temp_cmd = "./nvme dera state {0} | grep 'temperature_sensor' | cut -d ':' -f 2 | cut -d ' ' -f 2".format(nvme_dev)
        get_temp_cmd_output = os.popen(get_temp_cmd).readlines()
        sensor_temp = []
        for sensor in get_temp_cmd_output:  # 生成一个除0以外的温度列表，并由小到大排序
            sensor.strip('\n')
            sensor = int(sensor)
            if sensor == 0:
                continue
            else:
                sensor_temp.append(sensor)
        if not sensor_temp:
            return [0,0]
        else:
            sensor_temp.sort()
            return sensor_temp   # 返回一个由小到大排列的非零sensor温度列表
        # cpu_sensor = max(sensor_temp)
        # sensor_temp.remove(cpu_sensor)  # 弹出cpu温度
        # nand_max_temp = max(sensor_temp)    # 获取温度最高的nand温度值
        # print('current cpu temp is {0}'.format(cpu_sensor))
        # print('current nand max temp is {0}'.format(nand_max_temp))
        # return nand_max_temp

    def clr_mgcError():  # 清除mgc错误信息统计
        os.popen('./cleanMgcErrorInfo.sh')
        return

    def get_mgcError():  # 获取mgc错误信息统计
        
        mgc_num = ['#419b','#519b','#b19b','#c19b']
        mgc_error_info = []
        get_mgc_cmd = './nvme dera get-log /dev/nvme0'
        
        for mgc in mgc_num:
            mgc_ready_cmd = "./nvme dera uart-in -p '{0} 0 0' /dev/nvme0".format(mgc)
            os.popen(mgc_ready_cmd)
            time.sleep(1)
            get_current_mgc_error_info = os.popen(get_mgc_cmd).readlines()  # 获取当前mgc的error info 信息
            mgc_error_info.extend(get_current_mgc_error_info)   # 存储到mgc_error_info变量中
        
        return mgc_error_info

    def ssd_format(nvme_dev='/dev/nvme0'):    # 向SSD发送format命令并等待完成
        return_code = os.popen('./nvme format {0}'.format(nvme_dev)).readlines()
        if 'Success' in return_code[0]:
            print('ssd format success.')
            return
        else:
            print('ssd format error')
            return

    def wait_for_env_temp(temp,offset=3): # 等待环境温度到达预定值附近
        temp = int(temp)
        uppertemp = temp + offset
        lowertemp = temp - offset
        desired_range = range(lowertemp, uppertemp)
        current_temp = get_sensor_temp()[-2]
        env_temp = current_temp - 5
        # run = input('please confirm the chamber set to {0} and press enter to run'.format(temp))
        while env_temp not in desired_range:
            print('waitting for temp to {0}, current env temp is {1}.'.format(temp,str(env_temp)))
            time.sleep(10)
            current_temp = get_sensor_temp()[-2]
            env_temp = current_temp - 5
        print('The temperature reaching the predetermined value: {0}.'.format(env_temp))
        time.sleep(60) # 等待chamber环境温度趋于稳定，由于温箱温控误差，该值由经验来判断
        return

    def run_time_log(info=''):  # 脚本运行的记录
        now_time = datetime.datetime.now()
        readable_time = now_time.strftime('%Y-%m-%d %H:%M:%S')
        info_per_line = '{0}: {1}\n'.format(readable_time,info)
        with open('run_log.txt','a') as log:
            log.writelines(info_per_line)
        log.close()
            
    def list_to_csv(list_name, filename):   # 将数据转换为csv格式的文件
        # 检查列表是否为空
        if not list_name:
            print('list is empty.')
            return
        # 调用re.split()对list逐个字符元素进行分割，非字符元素将被丢弃
        selected_list = []
        # print(list_name) # kou debug...
        for list_line in list_name:
            selected = []
            if isinstance(list_line, str):
                pass
            else:
                print('worng type.')
                return
            list_line.strip('\n')
            if 'ERRBit' in list_line:   # 对ERRBit行的特殊处理
                splited = re.split(r'[.=,]', list_line) # 将长字符以 . , = 为分界，分解为列表
                if len(splited) < 10:
                    selected = [list_line]  
                else:
                    selected = [splited[5], splited[7], splited[9]]
                # print(splited)
            elif 'ERRUNC' in list_line: # 对 ERRUNC行的特殊处理
                splited = re.split(r'[.=,>]', list_line)
                if len(splited) < 10:
                    selected = [list_line] 
                else:
                    selected = ['>72', splited[7], splited[9]]
                # print(splited)
            elif 'TotalReadECCFrameCnt' in list_line:   # 对汇总行的特殊处理
                splited = re.split(r'[,=]', list_line)
                if len(splited) < 7:
                    selected = [list_line]
                else:
                    selected = ['Total',splited[2], splited[4]]
            elif 'cpu_mask' in list_line:   # 对起始行的特殊处理
                splited = re.split(r'[ ]', list_line)
                if len(splited) < 10:
                    selected = [list_line]
                else:
                    selected = ['cpu_mask', splited[9]]
            else:
                continue    # 如果行中不包含上述关键字，则该行信息被废弃，检测下一行
            # print(selected)    
            selected_list.append(selected)
        with open(filename,'a',newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['ErrBit','FrameCnt','Rate'])
            data = selected_list
            writer.writerows(data)
            csv_file.close()
        return

    def runIO(mode='r'): # 调用iovt对SSD做io，只针对3.2T SSD，随机在数据格式为0，1，4，LA中选择一种后续进行传参处理
        data_patten_pool = ['0','1','5','LA']
        data_patten = choice(data_patten_pool)
        seq_read_cmd = './iovt -t 4 -j 64 -w 0 -r 1 -s 2980G -b 128K -S -P {0}'.format(data_patten)
        seq_write_cmd = './iovt -t 4 -j 64 -w 1 -r 0 -s 2980G -b 128K -S -P {0}'.format(data_patten)

        if mode is 'r':
            print('start seq reading... data patten is {0}'.format(data_patten))
            os.system(seq_read_cmd)
        elif mode is 'w':
            print('start seq writing... data patten is {0}'.format(data_patten))
            os.system(seq_write_cmd)
        return
    
    
    """------ Test Start ------"""
    # temps = temp_sets()
    temps = [[25,25],[55,-20],[55,10],[55,0],[55,10],[-20,55],[-10,55],[0,55],[10,55]]
    run_time_log('Test Start. temp sets are {0}'.format(temps))

    for temp_set in temps:
        write_temp = temp_set[0]
        read_temp = temp_set[1]
        filename = '{0}-{1}.csv'.format(write_temp, read_temp)
        """------ Step 0 check env temp ------"""
        print('Test Start. current temp set is {0}|{1}'.format(write_temp,read_temp))
        run_time_log('{0}|{1} test prepare to run, checking env temp...'.format(write_temp,read_temp))
        print('Step0 Waitting for chamber temp to {0}'.format(write_temp))
        wait_for_env_temp(write_temp)
        print('Step0 complete.')
        run_time_log('env temp good, start test')
        """------ Step 1 format ssd ------"""
        message = 'Step1, start to format ssd...'
        print(message)
        ssd_format()
        message = 'Step1 complete.'
        print(message)
        run_time_log('ssd format complete')
        """------ Step 2 clr mgc error info ------"""
        print('Step2, start to clear mgc errors...')
        clr_mgcError()
        print('Step2 complete.')
        run_time_log('clr mgc error complete.')
        """------ Step 3 sequential write ------"""
        print('Step3 start to run seq write...')
        runIO('w')
        temp_after_write = get_sensor_temp()    # 将所有温度sensor的值写入log日志
        print('Step3 complete, current temp is {0}'.format(temp_after_write))
        run_time_log('seq write complete, current nand temp is {0}'.format(temp_after_write))
        """------ Step 4 change chamber env temp ------"""
        if write_temp != read_temp:
            print('Step4 waiting chamber change env temp...')
            wait_for_env_temp(read_temp)
            print('Step4 complete.')
            # run_time_log('read temp reaching. prepare to seq read')
        else:
            print('same temp testing, start seq read directly')
        run_time_log('read temp reaching. prepare to seq read')
        """------ Step 5 sequential read ------"""
        print('Step5 start to run seq read.')
        runIO('r')
        temp_after_read = get_sensor_temp()
        print('Step5 complete, current temp is {0}'.format(temp_after_read))
        run_time_log('seq read complete, current nand temp is {0}'.format(temp_after_read))
        """------ Step 6 get mgc error info ------"""
        print('Step6 start to get mgc error info...')
        list_name = get_mgcError()
        print('Step6 complete.')
        run_time_log('mgc info dump success, start to generate csv file...')
        """------ Step 7 process mgc error info ------"""
        print('Step7 process mgc error info')        
        list_to_csv(list_name, filename)
        print('Step7 complete.')
        run_time_log('creat csv file successfully. ')

        print('{0}|{1} test complete'.format(write_temp,read_temp))
        input('press enter to start next round.')
    run_time_log('all sets test complete.')          
main()

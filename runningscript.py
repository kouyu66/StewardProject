import time
import os

def checkRunningScript():

    """循环监控，每秒一次反馈当前测试机脚本运行状态，并获取脚本名及运行参数"""
    while True:

        running_script_ps = os.popen("ps -elf | grep -v 'grep' | grep -E '\./ts_.* | \./runio.*'").readlines()
        uptime = float(os.popen("cat /proc/uptime | cut -d ' ' -f 1").readlines()[0])    # 获取系统已经启动了多久 秒数

        if not running_script_ps:
            if uptime > 50:
                running_scripts = 0    # 无正在运行的脚本，且系统启动超过50秒可判断无脚本自启动
            else:
                running_scripts = 1    # 无正在运行的脚本，但系统启动没超过50秒，有可能后续会自行启动
        else:
            running_scripts = [steward_lib.findString(raw_script, '\./.*')[0].strip('\n') for raw_script in running_script_ps]  # 获取运行中脚本名以及参数
                    
checkRunningScript()
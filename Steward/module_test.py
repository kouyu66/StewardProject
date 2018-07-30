

node_info = ['/dev/nvme0', '/dev/nvme1', '/dev/nvme2']
scripts = [['runio.py', '/dev/nvme0n1 -l 100', '3994'],['runio.py', '/dev/nvme1n1 -l 100', '3995'],['runio.py', '/dev/nvme2n1 -l 100', '3996']]

for node in node_info:
    running_script = []
    for script in scripts:  # 获取当前设备的脚本信息

        if 'ts_pwr' in script[0] or 'ts_top' in script[0]:
            running_script = script
            break
        elif node in script[1]:  # 除掉电脚本外，特殊指明设备的脚本
            running_script = script
            break
        else:  # 无当前卡相关的脚本
            pass
    if not running_script:
        running_script = []

#!/usr/bin/env python3
# Coding:UTF-8
import os
import time

def env_check():
    # install dmidecode newer than v2.8
    # copy nvme tool
    # add script to rc.
    os.popen('cp -rf /system_repo/tools/dmidecode-3-1 /ge/auto')
    os.popen('cp -rf /system_repo/tools/nvme/nvme .')
    time.sleep(1)
    os.chdir('/ge/auto/dmidecode-3-1')
    os.popen('make && make install')
    
    return
env_check()
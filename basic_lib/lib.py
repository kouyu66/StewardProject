#!/usr/bin/env python3
# 用于linux平台的基础库

# 从列表中选择一项
def select_from_list(list_obj):
    '''根据用户输入，选择列表中元素（单选）'''
    if not list_obj:    # 空列表检查
        print('empty list detected. no selection is needed.')
        return 1
    
    for item in list_obj:   # 打印列表内容
        print(' {0} - {1}'.format(list_obj.index(item), item))
    
    user_select = input('\n select index from above\n > ')
    try:
        user_select_index = int(user_select)
        if user_select_index in range(0,len(list_obj)):
            result = list_obj[user_select_index]
            print('user select: {0}'.format(result))
            return result

        else:
            print('user select out of range.')
            return 1
    except Exception:   # 非法字符检查
        print('invalid input detected.')
        return 1

def multiThread(funcname, listname):
    """以列表中元素作为参数，列表元素数作为线程个数，多线程执行指定函数
    阻塞，当所有线程执行完成后才继续主线程"""
    threadIndex = range(len(listname))
    threads = []
    for num in threadIndex :
        t = threading.Thread(target=funcname, args=(listname[num],))
        threads.append(t)
    for num in threadIndex:
        threads[num].start()
    for num in threadIndex:
        threads[num].join()
    return

def multiThreadDeamon(funcname, listname):
    '''以列表中元素作为参数，列表元素个数作为线程数，多线程执行指定函数
    非阻塞，主线程不等待子线程执行结束，且主线程退出时，子线程立即退出'''
    threadIndex = range(len(listname))
    threads = []
    for num in threadIndex :
        t = threading.Thread(target=funcname, args=(listname[num],), daemon=True)
        threads.append(t)
    for num in threadIndex:
        threads[num].start()
    return
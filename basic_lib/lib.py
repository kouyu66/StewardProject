#!/usr/bin/env python3
# 用于linux平台的基础库

# 从列表中选择一项
def select_from_list(list_obj):
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

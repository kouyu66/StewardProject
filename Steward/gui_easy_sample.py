#!/usr/bin/env python3
# coding:utf-8
import tkinter

root = tkinter.Tk()
label = tkinter.Label(root, text='Dera System Test Monitor')
label.pack()
button1 = tkinter.Button(root, text='Dump To Excel')
button1.pack(side=tkinter.TOP, anchor='w')
# button2 = tkinter.Button(root, text='Button2')
# button2.pack(side=tkinter.RIGHT)
monitorfm = tkinter.Frame(root)
monitorsb = tkinter.Scrollbar(monitorfm)
monitorsb.pack(side=tkinter.RIGHT, fill=tkinter.Y)
monitordisplay = tkinter.Listbox(
    monitorfm, height=50, width=200, yscrollcommand=monitorsb.set)
# monitordisplay.bind()
monitorsb.config(command=monitordisplay.yview)
monitordisplay.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
monitorfm.pack()

# self.dirfm = Frame(self.top)    # 生成一个包含其他控件的容器
# self.dirsb = Scrollbar(self.dirfm)  # 生成滚动轴控件
# self.dirsb.pack(side=RIGHT, fill=Y) # 定义滚动轴位置
# self.dirs = Listbox(self.dirfm, height=50, width=900, yscrollcommand=self.dirsb.set) # 生成选项列表区域
# self.dirs.bind('<Double-l>', self.setDirAndGo)  # dir框架区域内双击条目将触发setDirAndGo函数
# self.dirsb.config(command=self.dirs.yview)  #将滚动轴与框架区域联系起来
# self.dirs.pack(side=LEFT, fill=BOTH)    # 定义选项列表区域位置
# self.dirfm.pack()   # 定义框架区域位置

root.mainloop()
#!/usr/bin/env python3
# Coding:UTF-8

import os
from time import sleep
from tkinter import *

class Monitor(object):

    def __init__(self, initdir=None):
        self.top = Tk() # 生成画布
        self.label = Label(self.top, text='System Test Monitor v0.1')   # 生成一个不需要交互的标签
        self.label.pack()   # 放对位置

        self.cwd = StringVar(self.top)  # 不明白...

        self.dirl = Label(self.top, fg='blue', font=('Helvetica', 12, 'bold'))
        self.dirl.pack()

        self.dirfm = Frame(self.top)    # 生成一个包含其他控件的容器
        self.dirsb = Scrollbar(self.dirfm)  # 生成滚动轴控件
        self.dirsb.pack(side=RIGHT, fill=Y) # 定义滚动轴位置
        self.dirs = Listbox(self.dirfm, height=50, width=900, yscrollcommand=self.dirsb.set) # 生成选项列表区域
        self.dirs.bind('<Double-l>', self.setDirAndGo)  # dir框架区域内双击条目将触发setDirAndGo函数
        self.dirsb.config(command=self.dirs.yview)  #将滚动轴与框架区域联系起来
        self.dirs.pack(side=LEFT, fill=BOTH)    # 定义选项列表区域位置
        self.dirfm.pack()   # 定义框架区域位置

        self.dirn = Entry(self.top, width=50, textvariable=self.cwd)    # 生成一个输入框
        self.dirn.bind('<Return>', self.doLS)   # 输入框绑定回车键，单击回车会调用doLS函数
        self.dirn.pack()    # 放置输入框

        self.bfm = Frame(self.top)  # 生成一个包含其他控件的容器
        self.clr = Button(self.bfm, text='Clear', command=self.clrDir, activeforeground='white', activebackground='white')   # 定义clear按钮，并关联到clrDir函数
        self.ls = Button(self.bfm, text='List Directory', command=self.doLS, activeforeground='white', activebackground='white')    # 定义ListDirectory按钮，并关联到doLS函数
        self.quit = Button(self.bfm, text='Quit', command=self.top.quit, activeforeground='white', activebackground='white')  # 定义Quit按钮，并关联到界面关闭函数
        self.clr.pack(side=LEFT)
        self.ls.pack(side=LEFT)
        self.quit.pack(side=LEFT)
        self.bfm.pack()

        if initdir:
            self.cwd.set(os.curdir)
            self.doLS()
    
    def clrDir(self, en=None):
        self.cwd.set('')

    def setDirAndGo(self, ev=None):
        self.last = self.cwd.get()
        self.dirs.config(selectbackground='red')
        check = self.dirs.get(self.dirs.curselection()) # 获取鼠标选中作为目录名
        if not check:
            check = os.curdir
        self.cwd.set(check)
        self.doLS()

    def doLS(self, ev=None):
        error = ''
        tdir = self.cwd.get()
        if not tdir:
            tdir = os.curdir
        if not os.path.exists(tdir):
            error = tdir + ': no such file'
        elif not os.path.isdir(tdir):
            error = tdir + ': not a directory'

        if error:
            self.cwd.set(error)
            self.top.update()
            sleep(2)
            if not (hasattr(self, 'last') and self.last):
                self.last = os.curdir
            self.cwd.set(self.last)
            self.dirs.config(selectbackground='LightSkyBlue')
            self.top.update()
            return
        
        self.cwd.set('Fetching Directory Contents...')
        self.top.update()
        dirlist = os.listdir(tdir)
        dirlist.sort()
        os.chdir(tdir)

        self.dirl.config(text=os.getcwd())
        self.dirs.delete(0, END)
        self.dirs.insert(END, os.curdir)
        self.dirs.insert(END, os.pardir)
        for eachFile in dirlist:
            self.dirs.insert(END, eachFile)
        self.cwd.set(os.curdir)
        self.dirs.config(selectbackground='LightSkyBlue')

def main():
    d = Monitor(os.curdir)
    mainloop()

if __name__ == '__main__':
    main()

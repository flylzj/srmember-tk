# coding: utf-8
from tkinter import Tk
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from queue import Queue
from tkinter.scrolledtext import ScrolledText


class FileFrame(tk.Frame):
    def __init__(self):
        super().__init__()
        self.filename = tk.StringVar(self, name="filename")
        self.file_path = tk.Entry(self, textvariable=self.filename)
        self.file_button = tk.Button(self, text="选择订单文件", command=self.show_filename)
        self.submit_button = tk.Button(self, text="开始验证信息")
        self.create()

    def show_filename(self):
        file = askopenfilename()
        if not file:
            return
        elif not file.endswith("xlsx"):
            tk.messagebox.showinfo(title="提示", message="文件格式错误")
            return
        self.setvar(name="filename", value=file)
        # self.file_path.insert(tk.END, self.getvar("filename"))

    def create(self):
        self.file_path.grid(row=0, column=1, sticky=tk.E)
        self.file_button.grid(row=1, column=1)
        self.submit_button.grid(row=2, column=1)


class AutherRoot(Tk):
    def __init__(self):
        super().__init__()
        self.msg_queue = Queue()
        self.file_frame = FileFrame()
        self.file_frame.pack()
        self.info_text = ScrolledText(self)
        self.info_text.pack()
        self.create()
        self.log_info()

    def log_info(self):
        if not self.msg_queue.empty():
            msg = self.msg_queue.get()
            self.info_text.insert(tk.END, msg)
        self.after(10, self.log_info)

    def delete_log_info(self):
        self.info_text.delete(1.0, tk.END)

    def create(self):
        self.file_frame.create()


if __name__ == '__main__':
    ar = AutherRoot()
    ar.mainloop()

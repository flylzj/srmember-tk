# coding: utf-8
import tkinter as tk
from tkinter.filedialog import askopenfilename
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText
from queue import Queue
from mytoken import Mytoken


class Root(tk.Tk):
    def __init__(self):
        super().__init__()
        self.mt = Mytoken()
        self.friends = None
        self.check()
        self.wm_title("自动下单")
        self .resizable(0, 0)
        self.msg_queue = Queue()
        self.account_frame = AccountFrame()
        self.file_frame = FileFrame()
        self.info_text = ScrolledText(self)
        self.create()
        self.log_info()

    def check(self):
        friends = self.mt.check()
        if not friends:
            tk.messagebox.showwarning(title="未授权", message="无权使用")
            tkinter.messagebox.showinfo(title="提示", message="请将这串代码发给管理员: " + self.mt.gene_d())
            exit()
        else:
            self.friends = friends
            tk.messagebox.showinfo(message="欢迎使用")

    def log_info(self):
        if not self.msg_queue.empty():
            msg = self.msg_queue.get()
            self.info_text.insert(tk.END, msg)
        self.after(10, self.log_info)

    def delete_log_info(self):
        self.info_text.delete(1.0, tk.END)

    def create(self):
        self.account_frame.pack()
        self.file_frame.pack()
        self.info_text.pack()


class AccountFrame(tk.Frame):
    def __init__(self):
        super().__init__()
        self.username = tk.StringVar(self, name="username")
        self.password = tk.StringVar(self, name="password")
        self.username_label = tk.Label(self, text="账号:")
        self.username_entry = tk.Entry(self, textvariable=self.username)
        self.password_label = tk.Label(self, text="密码:")
        self.password_entry = tk.Entry(self, textvariable=self.password)
        self.create()

    def create(self):
        self.username_label.grid(row=0, column=0)
        self.username_entry.grid(row=0, column=1)
        self.password_label.grid(row=0, column=2)
        self.password_entry.grid(row=0, column=3)


class FileFrame(tk.Frame):
    def __init__(self):
        super().__init__()
        self.filename = tk.StringVar(self, name="filename")
        self.file_path = tk.Entry(self, textvariable=self.filename)
        self.file_button = tk.Button(self, text="选择订单文件", command=self.show_filename)
        self.submit_button = tk.Button(self, text="开始自动下单")
        self.create()

    def show_filename(self):
        file = askopenfilename()
        if not file.endswith("xlsx"):
            tk.messagebox.showinfo(title="提示", message="文件格式错误")
            return
        self.setvar(name="filename", value=file)
        # self.file_path.insert(tk.END, self.getvar("filename"))

    def create(self):
        self.file_path.grid(row=0, column=0, sticky=tk.E)
        self.file_button.grid(row=0, column=1)
        self.submit_button.grid(row=0, column=2)


if __name__ == '__main__':
    root = Root()
    root.mainloop()
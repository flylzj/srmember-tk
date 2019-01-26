# coding: utf-8
import tkinter as tk
from mytoken import Mytoken
import tkinter.messagebox
import re


class TokenRoot(tk.Tk):
    def __init__(self):
        super().__init__()
        self.wm_title("token生成器")
        # self.geometry("300x200")
        self.mt = Mytoken()
        self.token_frame = TokenFrame()
        self.friend_frame = FriendFrame()
        self.token_frame.enter_button.configure(command=self.generate_token)
        self.friend_frame.pack()
        self.token_frame.pack()

    def generate_token(self):
        mac_id = self.getvar("mac_id")
        expired_time = self.getvar("expired_time")
        if not mac_id or not expired_time or not expired_time.isdigit():
            tk.messagebox.showwarning(title="", message="请输入正确格式的mac id或时间")
            return

        token = self.mt.generate_token(mac_id, self.get_friends(), 3600 * int(expired_time))
        if not token:
            tk.messagebox.showinfo(title="", message="生成失败")
            return
        try:
            self.mt.dump_to_file(token)
            tk.messagebox.showinfo(title="", message="生成成功")
        except Exception as e:
            tk.messagebox.showinfo(title="", message="生成失败, 请检查文件权限")

    def get_friends(self):
        friends = list(self.friend_frame.friend_listbox.get(0, tk.END))
        return friends


class TokenFrame(tk.Frame):
    def __init__(self):
        super().__init__()
        self.mac_id = tk.StringVar(name="mac_id")
        self.expired_time = tk.StringVar(name="expired_time")
        self.tip_label = tk.Label(self, text="请输入mac id:")
        self.mac_entry = tk.Entry(self, textvariable=self.mac_id)
        self.time_label = tk.Label(self, text="输入过期时间:")
        self.time_entry = tk.Entry(self, textvariable=self.expired_time)
        self.time_label2 = tk.Label(self, text="小时")
        self.enter_button = tk.Button(self, text="生成token")
        self.create()

    def create(self):
        self.tip_label.grid(row=0, column=0)
        self.mac_entry.grid(row=0, column=1)
        self.time_label.grid(row=1, column=0)
        self.time_entry.grid(row=1, column=1)
        self.time_label2.grid(row=1, column=2)
        self.enter_button.grid(row=2, column=2)


class FriendFrame(tk.Frame):
    def __init__(self):
        super().__init__()
        self.friend_phone = tk.StringVar(name="friend_phone")
        self.friend_label = tk.Label(self, text="委托人列表")
        self.friend_listbox = tk.Listbox(self)
        self.friend_entry = tk.Entry(self, textvariable=self.friend_phone)
        self.add_friend_button = tk.Button(self, text="添加委托人", command=self.add_friend)
        self.delete_friend_button = tk.Button(self, text="删除选中委托人", command=self.delete_friend)
        self.create()

    def create(self):
        self.friend_label.grid(row=0, column=0)
        self.friend_listbox.grid(row=1, column=0)
        self.friend_entry.grid(row=2, column=0)
        self.add_friend_button.grid(row=2, column=1)
        self.delete_friend_button.grid(row=2, column=2)

    def add_friend(self):
        friend_phone = self.getvar("friend_phone")
        if not friend_phone:
            return
        elif not re.search(r'1[0-9]{10}', friend_phone):
            tk.messagebox.showwarning(title="警告", message="电话号码格式错误!")
            self.setvar("friend_phone", "")
        else:
            self.friend_listbox.insert(tk.END, friend_phone)
            self.setvar("friend_phone", "")

    def delete_friend(self):
        try:
            self.friend_listbox.delete(self.friend_listbox.curselection())
        except Exception as e:
            tk.messagebox.showwarning(title="提示", message="删除失败")


if __name__ == '__main__':
    tr = TokenRoot()
    tr.mainloop()
# coding: utf-8
from auther_tk import AutherRoot
from excel import Excel
from tkinter import messagebox
import re
from address import check_address
from srmember import Srmember
from threading import Thread


class Auther(object):
    def __init__(self):
        self.ar = AutherRoot()
        self.excel = Excel()
        self.sr = Srmember()
        self.ar.file_frame.submit_button.configure(command=self.check_with_thread)
        self.msg_queue = self.ar.msg_queue

    def check_with_thread(self):
        t = Thread(target=self.check)
        t.setDaemon(True)
        t.start()

    def check(self):
        filename = self.ar.getvar('filename')
        if not filename:
            messagebox.showwarning(message="请选择文件")
            return
        try:
            sheet = self.excel.read_excel(filename)
            orders = self.excel.get_auther_orders(sheet)
        except Exception as e:
            messagebox.showwarning(message="文件内容错误")
            return
        self.ar.delete_log_info()
        for order in orders:
            self.check_info(order)
        self.msg_queue.put("验证结束\n")
        if not self.excel.save_auther_orders(orders):
            self.msg_queue.put("导出结果失败,请目录权限\n")
        self.msg_queue.put("已将结果导出为当前目录的out.xlsx, 请查看\n")

    def check_phone(self, tel):
        if not tel:
            return False
        elif not re.search(r'1[0-9]{10}', str(tel)):
            return False
        return True

    def check_good(self, good_info):
        good = self.sr.get_good_info(good_info.get("abiid"))
        if not good:
            return 1
        if good.get("abiid") != good_info.get("abiid"):
            return 1
        price = self.sr.get_good_price(good_info.get("abiid"))
        if good_info.get("price") != price:
            return 2
        self.msg_queue.put("商品id: {}=>{}\n商品名称: {}=>{}\n商品价格: {}=>{}\n".format(
            good_info.get("abiid"),
            good.get("abiid"),
            good_info.get("good_name"),
            good.get("mainname"),
            good_info.get("price"),
            price
        ))
        self.msg_queue.put("验证成功\n")

    def check_info(self, info):
        info["errors"] = {}
        start = "\n" + "*" * 20 + "开始验证" + "*" * 20 + "\n"
        end = "\n" + "*" * 20 + "结束验证" + "*" * 20 + "\n"
        self.msg_queue.put(start)

        self.msg_queue.put("\n正在验证电话是否正确\n")
        if self.check_phone(info.get("tel")):
            self.msg_queue.put("验证成功\n")
        else:
            self.msg_queue.put("验证失败\n")
            info["errors"]["tel_error"] = True

        self.msg_queue.put("\n正在验证地址信息\n")
        if check_address(str(info.get("address"))):
            self.msg_queue.put("验证成功\n")
        else:
            self.msg_queue.put("验证失败\n")
            info["errors"]["address_error"] = True

        self.msg_queue.put("\n正在验证商品信息\n")

        i = 1
        for good in info.get("goods"):
            self.msg_queue.put("\n正在验证商品{}\n".format(i))
            i += 1
            try:
                err = self.check_good(good)

                if err == 1:
                    self.msg_queue.put("商品不存在")
                    info["errors"]["good_error"] = True
                elif err == 2:
                    self.msg_queue.put("商品价格不匹配")
                    info["errors"]["price_error"] = True
            except Exception as e:
                self.msg_queue.put("网络错误\n")
                continue

        self.msg_queue.put(end)

    def run(self):
        self.ar.mainloop()


if __name__ == '__main__':
    auther = Auther()
    auther.run()


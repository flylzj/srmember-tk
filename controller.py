# coding: utf-8
from excel import Excel
from srmember import Srmember
from srmember_tk import Root
from threading import Thread
from address import check_address


class Controller:
    def __init__(self):
        self.star = "*" * 20
        self.order_start_line = self.star + "订单开始" + self.star + "\n\n"
        self.order_end_line = "\n" + self.star + "订单结束" + self.star + "\n\n"
        self.exceler = Excel()
        self.srmember = Srmember()
        self.window = Root()
        self.window.file_frame.submit_button.configure(command=self.start_order_with_thread)

    def start_order_with_thread(self):
        t = Thread(target=self.start_order)
        t.setDaemon(True)
        t.start()

    def start_order(self):
        self.window.delete_log_info()
        msg_queue = self.window.msg_queue
        if not self.srmember_login():
            return
        orders = self.read_excel()
        if not orders:
            return
        for order in orders:
            msg_queue.put(self.order_start_line)
            if not self.check_order_address(order):
                msg_queue.put(self.order_end_line)
                continue

            if not self.clear_shopcart():
                msg_queue.put(self.order_end_line)
                continue

            if not self.add_to_shopcart(order):
                msg_queue.put(self.order_end_line)
                continue

            order_id = self.create_order(order)
            if not order_id:
                msg_queue.put(self.order_end_line)
                continue

            friend_id = self.get_friend(order)
            if not friend_id:
                continue

            if not self.order_to_friend(order_id, friend_id, order):
                msg_queue.put(self.order_end_line)
                continue
            else:
                msg_queue.put("下单成功\n")

            msg_queue.put(self.order_end_line)
        msg_queue.put("自动下单完成")

    def srmember_login(self):
        msg_queue = self.window.msg_queue
        username = self.window.getvar("username")
        password = self.window.getvar("password")
        msg_queue.put(self.star + "账号信息" + self.star + "\n")

        msg_queue.put("账号: {}\n密码: {}\n".format(username, password))
        msg_queue.put("正在登录\n")
        try:
            self.srmember.login(username, password)
            msg_queue.put("登录成功\n")
            return True
        except Exception as e:
            msg_queue.put("登录失败, 请检查用户名密码, {}\n".format(e))
            msg_queue.put("自动下单完成\n")
            return False

    def read_excel(self):
        msg_queue = self.window.msg_queue
        filename = self.window.getvar("filename")
        data = self.exceler.myorders(filename)
        self.window.msg_queue.put(data.get("msg"))
        if data.get("code") != 0:
            return None
        orders = data.get("data")
        return orders

    def check_order_address(self, order):
        msg_queue = self.window.msg_queue
        msg_queue.put("当前订单为item {}\n".format(order.get("item")))
        msg_queue.put("正在检查订单地址信息\n")
        if not check_address(order.get("address")):
            msg_queue.put("地址有误\n")
            return False
        msg_queue.put("地址校验成功\n")
        return True

    def clear_shopcart(self):
        msg_queue = self.window.msg_queue
        msg_queue.put("正在清空购物车\n")
        try:
            self.srmember.clear_shopcart()
            msg_queue.put("清空购物车成功\n")
            return True
        except Exception as e:
            msg_queue.put("清空购物车失败 {}\n".format(e))
            return False

    def add_to_shopcart(self, order):
        msg_queue = self.window.msg_queue
        goods = order.get("goods")
        for good in goods:
            try:
                self.srmember.post_shopcart(good.get("abiid"), good.get("num"))
                good_info = self.srmember.get_good_info(good.get("abiid"))
                if good_info.get("abiid") != good.get("abiid"):
                    msg_queue.put("商品不存在!\n")
                    return False
                good_name = good_info.get("mainname") if good_info.get("mainname") else good.get("good_name")
                msg_queue.put("添加数量为 {} 的 {} 到购物车成功\n".format(good.get("num"), good_name))
            except Exception as e:
                msg_queue.put("添加数量为 {} 的 {} 到购物车失败, {}\n".format(good.get("num"), good.get("good_name"), e))
                return False
        return True

    def create_order(self, order):
        msg_queue = self.window.msg_queue
        goods = order.get("goods")
        abiid_list = [good.get("abiid") for good in goods]
        try:
            msg_queue.put("正在创建订单\n")
            data = self.srmember.create_order(abiid_list)
            if not data.get("success"):
                msg_queue.put("订单创建失败, {}\n".format(data.get("error")))
                self.window.msg_queue.put(self.star + "订单结束" + self.star + "\n\n")
                return False
            else:
                order_id = data.get("data").get("OBI_ID")
                msg_queue.put("订单创建成功\n")
                msg_queue.put("订单信息:\n")
                msg_queue.put("OBI_Amount: {}\nOBD_Now_Price: {}\n".format(
                    data.get("data").get("OBI_Amount"), data.get("data").get("OBD_Now_Price"))
                )
                return order_id
        except Exception as e:
            msg_queue.put("订单创建失败, {}\n".format(e))
            self.window.msg_queue.put(self.star + "订单结束" + self.star + "\n\n")
            return False

    def get_friend(self, order):
        msg_queue = self.window.msg_queue
        try:
            msg_queue.put("正在获取委托人id\n")
            friend = self.srmember.get_vip_friend(order.get("friend_phone"))
            if not friend:
                msg_queue.put("委托人id获取失败,请检查好友关系\n")
                return False
            msg_queue.put("获取好友成功,id:{}, nickname:{}\n".format(friend.get("id"), friend.get("nickname")))
            return friend.get("id")
        except Exception as e:
            msg_queue.put("委托人id获取失败,请检查好友关系, {}\n".format(e))
            self.window.msg_queue.put("order_end_line")
            return False

    def order_to_friend(self, order_id, friend_id, order):
        msg_queue = self.window.msg_queue
        try:
            msg_queue.put("开始下单\n")
            data = self.srmember.buy_by_friend(
                order_id, friend_id, order.get("name"), order.get("tel"), order.get("address")
            )
            if data.get("success"):
                return True
            else:
                msg_queue.put("下单失败 {}\n".format(data.get("error")))
                return False
        except Exception as e:
            msg_queue.put("下单失败 {}\n".format(e))
            return False

    def run(self):
        self.window.mainloop()


if __name__ == '__main__':
    c = Controller()
    c.run()
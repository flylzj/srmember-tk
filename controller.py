# coding: utf-8
from excel import Excel
from srmember import Srmember
from srmember_tk import Root
from threading import Thread


class Controller:
    def __init__(self):
        self.star = "*" * 20
        self.exceler = Excel()
        self.srmember = Srmember()
        self.window = Root()
        self.window.file_frame.submit_button.configure(command=self.start_order_with_thread)

    def start_order_with_thread(self):
        t = Thread(target=self.start_order)
        t.setDaemon(True)
        t.start()

    def start_order(self):
        msg_queue = self.window.msg_queue
        username = self.window.getvar("username")
        password = self.window.getvar("password")
        msg_queue.put(self.star + "账号信息" + self.star + "\n")

        msg_queue.put("账号: {}\n密码: {}\n".format(username, password))
        msg_queue.put("正在登录\n")
        try:
            self.srmember.login(username, password)
            self.window.msg_queue.put("登录成功\n")
        except Exception as e:
            self.window.msg_queue.put("登录失败, 请检查用户名密码, {}\n".format(e))
            msg_queue.put("自动下单完成")
            return
        filename = self.window.getvar("filename")
        data = self.exceler.myorders(filename)
        self.window.msg_queue.put(data.get("msg"))
        if data.get("code") != 0:
            return
        orders = data.get("data")
        for order in orders:
            self.window.msg_queue.put(self.star + "订单开始" + self.star + "\n")
            msg_queue.put("正在清空购物车\n")
            try:
                self.srmember.clear_shopcart()
            except Exception as e:
                msg_queue.put("清空购物车失败 {}\n".format(e))

            goods = order.get("goods")
            for good in goods:
                try:
                    self.srmember.post_shopcart(good.get("abiid"), good.get("num"))
                    msg_queue.put("添加数量为 {} 的 {} 到购物车成功\n".format(good.get("num"), good.get("abiid")))
                except Exception as e:
                    msg_queue.put("添加数量为 {} 的 {} 到购物车失败, {}\n".format(good.get("num"), good.get("abiid"), e))

            abiid_list = [good.get("abiid") for good in goods]
            try:
                msg_queue.put("正在创建订单\n")
                order_id = self.srmember.create_order(abiid_list)
                msg_queue.put("订单创建成功\n")
            except Exception as e:
                msg_queue.put("订单创建失败, {}\n".format(e))
                self.window.msg_queue.put(self.star + "订单结束" + self.star + "\n\n")
                continue
            try:
                msg_queue.put("正在获取委托人id\n")
                friend = self.srmember.get_vip_friend(order.get("friend_phone"))
                if not friend:
                    msg_queue.put("委托人id获取失败,请检查好友关系\n")
                    continue
                msg_queue.put("获取好友成功,id:{}, nickname:{}\n".format(friend.get("id"), friend.get("nickname")))
            except Exception as e:
                msg_queue.put("委托人id获取失败,请检查好友关系, {}\n".format(e))
                self.window.msg_queue.put(self.star + "订单结束" + self.star + "\n\n")
                continue
            try:
                msg_queue.put("开始下单\n")
                data = self.srmember.buy_by_friend(
                    order_id, friend.get("id"), order.get("name"), order.get("tel"), order.get("address")
                )
                msg_queue.put(data + "\n")
            except Exception as e:
                msg_queue.put("下单失败 {}\n".format(e))
            msg_queue.put("已完成 {} 发送至 {} 的订单\n".format(order.get("name"), order.get("address")))
            msg_queue.put(self.star + "订单结束" + self.star + "\n\n")
        msg_queue.put("自动下单完成")

    def run(self):
        self.window.mainloop()


if __name__ == '__main__':
    c = Controller()
    c.run()
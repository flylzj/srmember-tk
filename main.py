# # coding: utf-8
# from excel import Excel
# from srmember import Srmember
# from pprint import pprint
#
#
# class Controller:
#     def __init__(self):
#         self._excel = Excel()
#         self._srmember = Srmember()
#         self._srmember.login("15170307370", "lzjlzj123")
#
#     def start(self, filename):
#         orders = self._excel.myorders(filename)
#         if not orders:
#             print("读取文件失败")
#             return
#         for order in orders:
#             goods = order.get("goods")
#             for good in goods:
#                 good["abiid"] = self._srmember.search_good(good.get("good_name"))
#         for order in orders:
#             self._srmember.make_a_order(order.get("goods"), order.get("friend_phone"), order)
#
#
# if __name__ == '__main__':
#     c = Controller()
#     c.start("test.xlsx")
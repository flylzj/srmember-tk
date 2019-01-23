# coding: utf-8
from openpyxl import load_workbook


class Excel:
    def read_excel(self, filename):
        wb = load_workbook(filename)
        sheet = wb[wb.sheetnames[0]]
        return sheet

    def get_orders(self, sheet):
        orders = []
        for row in sheet.iter_rows(min_row=2):
            order = dict()
            order["friend_phone"] = str(row[0].value)
            order["name"] = row[1].value
            order["tel"] = str(row[2].value)
            order["address"] = row[3].value
            order["goods"] = []
            for i in range(4, len(row) - 1, 2):
                if not row[i].value:
                    continue
                order["goods"].append(
                    {
                        "abiid": row[i].value,
                        "num": row[i + 1].value
                    }
                )
            orders.append(order)
        return orders

    def myorders(self, filename):
        try:
            sheet = self.read_excel(filename)
        except Exception as e:
            return {
                "code": 1,
                "msg": "读取excel失败,请检查文件, {}\n".format(e)
            }
        try:
            orders = self.get_orders(sheet)
        except Exception as e:
            return {
                "code": 1,
                "msg": "读取订单失败,excel格式错误, {}\n".format(e)
            }
        return {
            "msg": "读取订单成功\n",
            "code": 0,
            "data": orders
        }


if __name__ == '__main__':
    filename = "test.xlsx"
    e = Excel()
    print(e.myorders(filename))

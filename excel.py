# coding: utf-8
from openpyxl import load_workbook
from pprint import pprint


class Excel:
    def __init__(self):
        self.sheet = None
        self.orders = []

    def read_excel(self, filename):
        try:
            wb = load_workbook(filename)
            self.sheet = wb[wb.sheetnames[0]]
        except Exception as e:
            print(e)

    def get_orders(self):
        for row in self.sheet.iter_rows(min_row=2):
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
                        "good_name": row[i].value,
                        "num": row[i + 1].value
                    }
                )
            self.orders.append(order)

    def myorders(self, filename):
        self.read_excel(filename)
        self.get_orders()
        return self.orders


if __name__ == '__main__':
    filename = "test.xlsx"
    e = Excel()
    e.myorders(filename)

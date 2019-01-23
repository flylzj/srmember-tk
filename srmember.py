# coding: utf-8
import hashlib
import requests
from random import randint
import time


class Srmember(object):
    def __init__(self):
        self._appsecret = 'e1d0b361201e4324b37c968fb71f0d3c'
        self._appid = "sunrise_member"
        self.login_api = "https://srmemberapp.srgow.com/user/loginv2"
        self.token_api = "http://srmemberapp.srgow.com/sys/token"
        self.shopcart_api = "https://srmemberapp.srgow.com/goods/shopcart"
        self.vip_api = "https://srmemberapp.srgow.com/relation/vip"
        self.order_api = "https://srmemberapp.srgow.com/order/createv2/"
        self.buy_api = "https://srmemberapp.srgow.com/order/wish/tomall"
        self.search_api = "https://srmemberapp.srgow.com/goods/search/1"
        self.token = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 4.4.2; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10) AppleWebKit"
                          "/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36 Html5Plus/1.0",
            "X-Requested-With": "XMLHttpRequest"
        }

    # 构造带token请求头
    def make_token_headers(self, user=False):
        headers = self.headers.copy()
        if not user:
            token = self.get_token()
            headers["Authorization"] = "Bearer {}".format(token)
        else:
            headers["Authorization"] = "Bearer {}".format(self.token)
        return headers

    # 获取token
    def get_token(self):
        _nonce = str(randint(1001, 10000))
        _timestamp = str(int(time.time()))
        _array = [_nonce, self._appsecret, _timestamp]
        _array.sort()
        _tmp = ''.join(_array)
        m = hashlib.md5(_tmp.encode())
        _signature = m.hexdigest().upper()
        data = {
            "appid": self._appid,
            "appsecret": self._appsecret,
            "timestamp": _timestamp,
            "signature": _signature,
            "nonce": _nonce
        }
        r = requests.post(self.token_api, headers=self.headers, data=data)
        d = r.json()
        token = d.get("data").get("token")
        return token

    # 获取md5值
    def md5(self, s):
        m = hashlib.md5()
        m.update(s.encode())
        return m.hexdigest()

    # 登录
    def login(self, username, password):
        data = {
            "tel": username,
            "pwd": self.md5(password).upper(),
            "devcode": "4ed59f36a2c9a887fc49a6eadc2f353c",
            "devmodel": "MIX 2",
            "devsys": "Android_8.0.0_zh_CN",
            "clientid": "4ed59f36a2c9a887fc49a6eadc2f353c"
        }
        headers = self.make_token_headers()
        headers["Content-Type"] = "application/json"
        r = requests.post(self.login_api, json=data, headers=headers)
        self.token = r.json().get("data").get("token").get("token")
        return True

    # 获取购物车里的商品
    def get_shopcart(self):
        headers = self.make_token_headers(user=True)
        r = requests.get(self.shopcart_api, headers=headers)
        try:
            datas = r.json().get("data")
            return datas
        except Exception as e:
            print(e)

    # 添加商品到购物车
    def post_shopcart(self, abiid, num):
        headers = self.make_token_headers(user=True)
        data = {
            "abiid": abiid,
            "num": num
        }
        requests.post(self.shopcart_api, headers=headers, json=data)

    def clear_shopcart(self):
        datas = self.get_shopcart()
        if not datas:
            return None
        for data in datas:
            self.post_shopcart(data.get("abiid"), 0)

    # 获取vip好友
    def get_vip_friend(self, phone):
        headers = self.make_token_headers(user=True)
        r = requests.get(self.vip_api, headers=headers)
        friends = r.json().get("data")
        for friend in friends:
            if friend.get("phone") == phone:
                return friend

    # 创建订单
    def create_order(self, abiid_list, remark=""):
        headers = self.make_token_headers(user=True)
        data = {
            "abiidList": abiid_list,
            "remark": remark
        }
        r = requests.post(self.order_api, json=data, headers=headers)
        print(r.json())
        return r.json().get("data").get("OBI_ID")

    # 委托好友
    def buy_by_friend(self, order_id, friend_id, name, tel, address):
        headers = self.make_token_headers(user=True)
        data = {
            "id": order_id,
            "uid": friend_id,
            "name": name,
            "tel": tel,
            "address": address
        }
        r = requests.post(self.buy_api, headers=headers, json=data)
        return r.text

    def make_a_order(self, goods, phone, user_info):
        self.clear_shopcart()
        for good in goods:
            self.post_shopcart(good.get("abiid"), good.get("num"))
        abiid_list = [good.get("abiid") for good in goods]
        order_id = self.create_order(abiid_list)
        friend_id = self.get_vip_friend(phone)
        if not friend_id or not order_id:
            print("好友不存在或订单创建失败")
            return
        self.buy_by_friend(order_id, friend_id, user_info.get("name"), user_info.get("tel"), user_info.get("address"))

    def search_good(self, key):
        params = {
            "a": "a",
            "key": key
        }
        headers = self.make_token_headers(user=True)
        r = requests.get(self.search_api, params=params, headers=headers)
        try:
            data = r.json().get("data")
            if not data:
                return None
            return data[0].get("abiid")
        except Exception as e:
            print(e)
            return None



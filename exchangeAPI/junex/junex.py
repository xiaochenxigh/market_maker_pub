import hashlib
import hmac
import base64
from operator import itemgetter
import aiohttp
import json
import logging


async def http_request(method, url, params=None, headers=None,auth=None):
    try:
        async with aiohttp.ClientSession(auth=auth) as session:
            if method == "GET":
                async with session.get(url, params=params, timeout=2.5) as response:
                    if response.status == 200:
                        response = await response.read()
                        return json.loads(response)
                    else:
                        logging.error('http_request_{}_{}_{}_{}'.format(method, url, params,await response.read()))
            if method == "POST":
                async with session.post(url, data=params, headers=headers, timeout=5) as response:
                    if response.status == 200:
                        response = await response.read()
                        return json.loads(response)
                    else:
                        logging.error('http_request_{}_{}_{}_{}'.format(method, url, params,await response.read()))
            if method == "PUT":
                async with session.put(url, data=params, headers=headers, timeout=2.5) as response:
                    if response.status == 200:
                        response = await response.read()
                        return json.loads(response)
                    else:
                        logging.error('http_request_{}_{}_{}_{}'.format(method, url, params,await response.read()))
            if method == "DELETE":
                async with session.delete(url, headers=headers, timeout=2.5) as response:
                    if response.status == 200:
                        response = await response.read()
                        return json.loads(response)
                    else:
                        logging.error('http_request_{}_{}_{}_{}'.format(method, url, params,await response.read()))
    except Exception as e:
        logging.error('http_request_{}_{}_{}'.format(url, params, e))
    return False


def produce_sign(secretkey, params={}):
    tempstr = str(params)
    dig = hmac.new(secretkey.encode('utf8'), tempstr.encode('utf8'), digestmod=hashlib.sha384).digest()
    sign = base64.b64encode(dig).decode()
    return sign


class Junex():
    def __init__(self, api_key, secret_key):
        self.apikey = api_key
        self.secretkey = secret_key

    # ticker
    async def ticker(self, symbol):
        path = "https://api.JUNEX.co:8323/api/v1/getticker"
        req = {
            "Symbol": symbol
        }
        headers = {
            "X-IDCM-APIKEY": self.apikey,
            "X-IDCM-SIGNATURE": produce_sign(self.secretkey, req),
            "X-IDCM-INPUT": str(req)
        }

        res = await http_request("POST", path, req, headers)

        if not res:
            return False

        if "data" in res:
            if res['data']:
                buy = res["data"]["buy"]
                sell = res["data"]["sell"]
                return [buy, sell]

    # depth
    async def depth_all(self, symbol):
        path = "https://api.JUNEX.co:8323/api/v1/getdepth"
        req = {
            "Symbol": symbol
        }

        headers = {
            "X-IDCM-APIKEY": self.apikey,
            "X-IDCM-SIGNATURE": produce_sign(self.secretkey, req),
            "X-IDCM-INPUT": str(req)
        }
        res = await http_request("POST", path, req, headers)

        if not res:
            return False

        buy_list = []
        sell_list = []
        if "data" in res:
            if res['data']:
                if "asks" in res["data"]:
                    for i in res["data"]["asks"]:
                        sell_list.append([i["price"], i["amount"]])
                if "bids" in res["data"]:
                    for i in res["data"]["bids"]:
                        buy_list.append([i["price"], i["amount"]])

        sell_list = sorted(sell_list, key=itemgetter(0))
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        return {"bids": buy_list, "asks": sell_list}

    # open_orders
    async def depth_my(self, symbol):
        path = "https://api.JUNEX.co:8323/api/v1/getorderinfo"
        req = {
            "Symbol": symbol,
            "OrderID": ""
        }
        headers = {
            "X-IDCM-APIKEY": self.apikey,
            "X-IDCM-SIGNATURE": produce_sign(self.secretkey, req),
            "X-IDCM-INPUT": str(req)
        }
        res = await http_request("POST", path, req, headers)

        if not res:
            return False

        buy_list = []
        sell_list = []
        if "data" in res:
            for i in res["data"]:
                order_id = i["orderid"]
                price = i["price"]
                amount = i["amount"]
                if i["side"] == 0:
                    buy_list.append([price, order_id, amount])
                if i["side"] == 1:
                    sell_list.append([price, order_id, amount])

        sell_list = sorted(sell_list, key=itemgetter(0))
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        return {"bids": buy_list, "asks": sell_list}

    # create_order
    async def create_order(self, symbol, price, amount, side):
        """0 买入，1，卖出"""
        path = "https://api.JUNEX.co:8323/api/v1/trade"
        req = {
            "Symbol": symbol,
            "Size": amount,
            "Price": price,
            "Side": side,
            "Type": 1,
            "Amount": amount
        }
        headers = {
            "X-IDCM-APIKEY": self.apikey,
            "X-IDCM-SIGNATURE": produce_sign(self.secretkey, req),
            "X-IDCM-INPUT": str(req)
        }
        res = await http_request("POST", path, req, headers)
        if res:
            print('order', symbol, price, amount, side, res['result'])
        else:
            print('order', symbol, price, amount, side, res)

    # cancel_order
    async def cancel_order(self, symbol, order_id, side):
        path = "https://api.JUNEX.co:8323/api/v1/cancel_order"
        req = {
            "Symbol": symbol,
            "OrderID": order_id,
            "Side": side
        }
        headers = {
            "X-IDCM-APIKEY": self.apikey,
            "X-IDCM-SIGNATURE": produce_sign(self.secretkey, req),
            "X-IDCM-INPUT": str(req)
        }
        res = await http_request("POST", path, req, headers)
        print('cancel', order_id, side, res["result"])

    # balances
    async def balances(self):
        path = "https://api.JUNEX.co:8323/api/v1/getuserinfo"
        req = 1
        headers = {
            "X-IDCM-APIKEY": self.apikey,
            "X-IDCM-SIGNATURE": produce_sign(self.secretkey, req),
            "X-IDCM-INPUT": str(req)
        }
        res = await http_request("POST", path, req, headers)
        bal = {}
        if "data" in res:
            for i in res["data"]:
                symbol = i["code"]
                free = i["free"]
                freeze = i["freezed"]
                if free + freeze > 0.0:
                    bal[symbol] = {"free": free, "freeze": freeze}
        return bal


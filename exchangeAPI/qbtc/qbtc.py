import asyncio
import time
import aiohttp
import json
import hashlib
from operator import itemgetter


def produce_sign(apikey, secretkey, params={}):
    strx = ''
    for k in sorted(params):
        strx += k + str(params[k])
    strx = secretkey + strx
    sign = hashlib.md5(strx.encode('utf-8')).hexdigest()
    return sign


async def http_request(method, url, params, headers=None):
    async with aiohttp.ClientSession() as session:
        if method == "GET":
            async with session.get(url, params=params, headers=headers, timeout=2.5) as response:
                response = await response.read()

                return json.loads(response)
        if method == "POST":
            async with session.post(url, data=params, headers=headers, timeout=2.5) as response:
                response = await response.read()
                return json.loads(response)


class Qbtc():
    def __init__(self, apikey, secretkey):
        self.__apikey = apikey
        self.__secretkey = secretkey

    async def depth_my(self, symbol):
        path = "https://www.qbtc.ink/api/getUnfinishedOrders"
        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

        req = {
            "coin": symbol.split('_')[0],
            "market": symbol.split('_')[1]
        }
        req["sign"] = produce_sign(self.__apikey, self.__secretkey, req)
        req["accessKey"] = self.__apikey
        req["reqTime"] = int(time.time() * 1000)
        res = await http_request("POST", path, req, h)

        if not res:
            return False

        buy_list = []
        sell_list = []
        if 'result' in res:
            for i in res['result']:
                price = float(i['price'])
                amount = float(i['total_amount'])
                order_id = i['entrustId']
                if i['tradeType'] == 2:
                    sell_list.append([price, order_id, amount])
                if i['tradeType'] == 1:
                    buy_list.append([price, order_id, amount])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))

        return {'bids': buy_list, 'asks': sell_list}

    async def balances(self):
        path = "https://www.qbtc.ink/api/showUser"
        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

        req = {}

        req["sign"] = produce_sign(self.__apikey, self.__secretkey, req)
        req["accessKey"] = self.__apikey
        req["reqTime"] = int(time.time() * 1000)
        res = await http_request("POST", path, req, h)
        if not res:
            return False
        bal = {}
        if 'result' in res:
            if 'coins' in res['result']:

                for i in res['result']['coins']:
                    coin = i['shortName']
                    free = float(i['balance'])
                    freeze = float(i['blockBalance'])
                    if free + freeze > 0:
                        bal[coin] = {"free": free, "freeze": freeze}
        return bal

    async def create_order(self, symbol, price, amount, side):
        path = "https://www.qbtc.ink/api/order"
        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

        req = {
            "tradeType": side,
            "price": price,
            "amount": amount,
            "coin": symbol.split('_')[0],
            "market": symbol.split('_')[1]

        }
        req["sign"] = produce_sign(self.__apikey, self.__secretkey, req)
        req["accessKey"] = self.__apikey
        req["reqTime"] = int(time.time() * 1000)
        res = await http_request("POST", path, req, h)
        print(req, res)

    async def cancel_order(self, order_id):
        path = "https://www.qbtc.ink/api/cancelOrder"
        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

        req = {
            "entrustId": order_id
        }
        req["sign"] = produce_sign(self.__apikey, self.__secretkey, req)
        req["accessKey"] = self.__apikey
        req["reqTime"] = int(time.time() * 1000)
        res = await http_request("POST", path, req, h)

    async def depth_all(self, symbol):
        path = 'https://www.qbtc.ink/json/depthTable.do'  # ?tradeMarket={}&symbol={}'.format(symbol.split('_')[0],symbol.split('_')[1])
        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        req = {
            'tradeMarket': symbol.split('_')[1],
            'symbol': symbol.split('_')[0]
        }
        res = await http_request("POST", path, req, h)

        buy_list = []
        sell_list = []
        if 'result' in res:
            if 'buy' in res['result']:
                for i in res['result']['buy']:
                    buy_list.append([float(i['price']), float(i['amount'])])
            if 'sell' in res['result']:
                for i in res['result']['sell']:
                    sell_list.append([float(i['price']), float(i['amount'])])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {"bids": buy_list, "asks": sell_list}


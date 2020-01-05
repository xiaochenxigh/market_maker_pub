import asyncio
import time
import requests
import aiohttp
import json
import datetime
from operator import itemgetter

import redis

red = redis.Redis(host='localhost', port=6379)


async def http_request(method, url, params, headers=None):
    async with aiohttp.ClientSession() as session:
        if method == "GET":
            async with session.get(url, params=params, headers=headers, timeout=2.5) as response:
                response = await response.read()

                return json.loads(response)
        if method == "POST":
            async with session.post(url, data=params, headers=headers, timeout=5) as response:
                response = await response.read()
                return json.loads(response)


async def get_symbol_id():
    path = "https://www.chaoex.info/unique/" + "coin/allCurrencyRelations"
    h = {
        "Content-Type": "application/x-www-form-urlencoded",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    res = await http_request("GET", path, {}, h)

    if res['attachment']:
        for i in res['attachment']:
            print(i)


class Chaoex():
    def __init__(self, user_id, token):
        self.__user_id = 0
        self.__token = 'x'
        if user_id == '749185':
            self.__user_id = int(json.loads(red.get('uid85')))
            self.__token = json.loads(red.get('token85'))
        if user_id == '749183':
            self.__user_id = int(json.loads(red.get('uid83')))
            self.__token = json.loads(red.get('token83'))

    async def balances(self):
        path = "https://www.chaoex.info/unique/" + "coin/customerCoinAccount"
        req = {
            "token": self.__token,
            "uid": self.__user_id,
            "local": "en_US",
            "timestamp": str(int(round(time.time() * 1000)))
        }
        h = {
            "Content-Type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }

        # res = requests.post(path,data=req,headers=h)
        # print(res.json())
        res = await http_request("POST", path, req, h)
        # print(res)
        bal = {}
        if 'attachment' in res:
            if 'coinList' in res['attachment']:
                for i in res['attachment']['coinList']:
                    symbol = i['currencyNameEn']
                    amount = float(i['amount'])
                    freeze = float(i['freezeAmount'])
                    if amount + freeze > 0:
                        bal[symbol] = {'free': amount, 'freeze': freeze}
        return bal

    async def create_order(self, symbol, price, amount, side):
        """
        1 buy
        2 sell
        """
        path = "https://www.chaoex.info/unique/" + "order/order"
        req = {
            "buyOrSell": side,
            "baseCurrencyId": 3,
            "currencyId": 229,
            "fdPassword": "",
            "num": amount,
            "price": price,
            "source": 5,
            "type": 1,
            "token": self.__token,
            "uid": self.__user_id,
            "local": "en_US",
            "timestamp": str(int(round(time.time() * 1000)))
        }
        h = {
            "Content-Type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }
        res = await http_request("POST", path, req, h)
        print("ORDER", symbol, price, amount, side, res)

    async def cancel_order(self, order_id):
        """
        1 buy
        2 sell
        """
        path = "https://www.chaoex.info/unique/" + "order/cancel"
        req = {
            "currencyId": 3,
            "orderNo": str(order_id),
            "fdPassword": "",
            "source": 5,
            "token": str(self.__token),
            "uid": str(self.__user_id),
            "local": "en_US",
            "timestamp": str(int(round(time.time() * 1000)))
        }
        h = {
            "Content-Type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }
        res = await http_request("POST", path, req, h)
        print("CANCEL", order_id, res['message'])

    async def depth_my(self, symbol):
        path = "https://www.chaoex.info/unique/" + "user/trOrderListByCustomer"
        req = {
            "beginTime": "2018-04-25",
            "endTime": "2050-04-25",
            "start": '1',
            "size": '50',
            "status": '11',
            "buyOrSell": '0',
            "baseCurrencyId": 3,
            "currencyId": 229,
            "priceType": 0,
            "token": self.__token,
            "uid": self.__user_id,
            "local": "en_US",
            "timestamp": str(int(round(time.time() * 1000)))
        }
        h = {
            "Content-Type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }
        res = await http_request("POST", path, req, h)
        buy_list = []
        sell_list = []
        if not res:
            return {"bids": buy_list, "asks": sell_list}
        if res['attachment']:
            if 'list' in res['attachment']:
                for i in res['attachment']['list']:
                    price = float(i['price'])
                    amount = float(i['remainNum'])
                    order_id = i['orderNo']
                    if i['buyOrSell'] == 1:
                        buy_list.append([price, order_id, amount])
                    if i['buyOrSell'] == 2:
                        sell_list.append([price, order_id, amount])
        if len(buy_list):
            buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        if len(sell_list):
            sell_list = sorted(sell_list, key=itemgetter(0))
        return {'bids': buy_list, 'asks': sell_list}

    @staticmethod
    async def ticker(symbol):
        path = "https://www.chaoex.info/unique/" + "quote/v2/realTime"
        req = {
            "coins": symbol
        }
        h = {
            "Content-Type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }
        res = await http_request("GET", path, req, h)
        if res['attachment']:
            data = res['attachment']
            return [data['buy'], data['sell'], data['last']]

    @staticmethod
    async def depth_all(symbol):
        path = "https://www.chaoex.info/unique/" + "quote/tradeDeepin"
        req = {
            "baseCurrencyId": 3,
            "tradeCurrencyId": 229,
            "limit": 10
        }
        h = {
            "Content-Type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }
        res = await http_request("GET", path, req, h)
        # print(res)
        buy_list = []
        sell_list = []
        if 'attachment' in res:
            data = res['attachment']
            if not data:
                return {"bids": buy_list, "asks": sell_list}
            if 'bids' in data:
                for i in data['bids']:
                    buy_list.append([float(i[0]), float(i[1])])
            if 'asks' in data:
                for i in data['asks']:
                    sell_list.append([float(i[0]), float(i[1])])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {"bids": buy_list, "asks": sell_list}

    @staticmethod
    async def history(symbol):
        path = "https://www.chaoex.info/unique/" + "quote/tradeHistory"
        req = {
            "baseCurrencyId": 3,
            "tradeCurrencyId": 229,
            "limit": 10
        }
        h = {
            "Content-Type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }
        res = await http_request("GET", path, req, h)
        if 'attachment' in res:
            data = res['attachment']
            if not data:
                return False
            timestamp = int(int(data[0]['date']) / 1000)
            dateArray = datetime.datetime.utcfromtimestamp(timestamp)
            otherStyleTime = dateArray.strftime("%Y--%m--%d %H:%M:%S")
            return otherStyleTime, int(data[0]['price'])


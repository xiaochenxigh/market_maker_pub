import aiohttp
import asyncio
import json
import uuid
import time
from decimal import Decimal
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



class Hitbtc():
    def __init__(self, api_key, secret_key):
        self.__url = 'https://api.hitbtc.com/api/2'
        self.__api_key = api_key
        self.__secret_key = secret_key

    async def get_symbol(self, symbol):
        path = self.__url + '/public/symbol'
        req = {
            'symbol': symbol
        }
        auth = aiohttp.BasicAuth(self.__api_key, self.__secret_key)
        res = await http_request("GET", path, req, auth=auth)
        print(res)

    async def balances(self):
        path = self.__url + '/trading/balance'
        req = {}
        auth = aiohttp.BasicAuth(self.__api_key, self.__secret_key)
        res = await http_request("GET", path, req, auth=auth)
        if not res:
            return False

        bal = {}
        if isinstance(res, list):
            for i in res:
                free = float(i['available'])
                freeze = float(i['reserved'])
                if free + freeze > 0:
                    bal[i['currency']] = {'free': free, 'freeze': freeze}
            return bal

    async def depth_all(self, symbol):
        path = self.__url + '/public/orderbook/' + symbol
        req = {}
        auth = aiohttp.BasicAuth(self.__api_key, self.__secret_key)
        res = await http_request("GET", path, req, auth=auth)

        if not res:
            return False

        buy_list = []
        sell_list = []
        if isinstance(res, dict):
            if 'ask' in res:
                for i in res['ask']:
                    price = float(i['price'])
                    amount = float(i['size'])
                    sell_list.append([price, amount])
            if 'bid' in res:
                for i in res['bid']:
                    price = float(i['price'])
                    amount = float(i['size'])
                    buy_list.append([price, amount])

        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {"bids": buy_list, "asks": sell_list}

    async def depth_my(self, symbol):
        path = 'https://api.hitbtc.com/api/2/order'
        req = {}
        auth = aiohttp.BasicAuth(self.__api_key, self.__secret_key)
        res = await http_request("GET", path, req, auth=auth)
        if res is False:
            return False

        buy_list = []
        sell_list = []
        if isinstance(res, list):
            for i in res:
                order_id = i['clientOrderId']
                price = float(i['price'])
                amount = float(i['quantity'])
                if i['side'] == 'buy':
                    buy_list.append([price, order_id, amount])
                if i['side'] == 'sell':
                    sell_list.append([price, order_id, amount])

        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {"bids": buy_list, "asks": sell_list}

    async def create_order(self, symbol, price, amount, side):
        path = self.__url + '/order/'
        req = {
            "symbol": symbol,
            "price": price,
            "quantity": amount,
            "side": side
        }

        auth = aiohttp.BasicAuth(self.__api_key, self.__secret_key)
        res = await http_request("POST", path, req, auth=auth)
        print("ORDER", symbol, price, amount, side, res)

    async def cancel_order(self, client_order_id):
        path = self.__url + '/order/' + client_order_id
        auth = aiohttp.BasicAuth(self.__api_key, self.__secret_key)
        res = await http_request("DELETE", path, auth=auth)
        print('CANCEL', client_order_id, res)


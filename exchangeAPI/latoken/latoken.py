import hashlib
import hmac
import time
import aiohttp
import json
from operator import itemgetter

base_url = 'https://api.latoken.com'


async def http_request(method, url, params=None, headers=None, api_key=None, secret_key=None):
    async with aiohttp.ClientSession() as session:
        if method == "GET":
            async with session.get(url, params=params, headers=headers, timeout=5) as response:
                if response.status == 200:
                    response = await response.read()
                    return json.loads(response)
        if method == "POST":
            async with session.post(url, data=params, headers=headers, timeout=2.5) as response:
                if response.status == 200:
                    response = await response.read()
                    return json.loads(response)
        if method == "PUT":
            async with session.put(url, data=params, headers=headers, timeout=2.5) as response:
                if response.status == 200:
                    response = await response.read()
                    return json.loads(response)
        if method == "DELETE":
            async with session.delete(url, headers=headers, timeout=2.5) as response:
                if response.status == 200:
                    response = await response.read()
                    return json.loads(response)


def produce_sign(resource_url, secret_key, params):
    sign_str = ''
    for k in sorted(params):
        sign_str += k + '=' + str(params[k]) + '&'
    query = '?' + sign_str[:-1]
    sign_str = resource_url + '?' + sign_str[:-1]
    return query, hmac.new(secret_key.encode('utf8'), sign_str.encode('utf8'), digestmod=hashlib.sha256).hexdigest()


# https://api.latoken.com/api/v1/MarketData/orderBook/ETHUSDT
class Latoken:
    def __init__(self, api_key, secret_key):
        self.__base_url = 'https://api.latoken.com'
        self.__api_key = api_key
        self.__secret_key = secret_key

    async def balances(self):
        path = '/api/v1/Account/balances'
        req = {
            'timestamp': int(time.time() * 1000)
        }
        query, sign = produce_sign(path, self.__secret_key, req)
        h = {
            'X-LA-KEY': self.__api_key,
            'X-LA-SIGNATURE': sign,
            'X-LA-HASHTYPE': 'HMAC-SHA256'
        }
        res = await http_request('GET', self.__base_url + path + query, headers=h)
        if res is False:
            return False
        bal = {}
        if isinstance(res, list):
            for i in res:
                free = float(i['available'])
                freeze = float(i['frozen'])
                if free + freeze > 0:
                    bal[i['symbol']] = {'free': free, 'freeze': freeze}
        return bal

    async def depth_all(self, symbol):
        path = '/api/v1/MarketData/orderBook/{}'.format(symbol)
        res = await http_request('GET', self.__base_url + path)
        if res is False:
            return False

        buy_list = []
        sell_list = []
        if isinstance(res, dict):
            if 'asks' in res:
                if res['asks'] is not None:
                    for i in res['asks']:
                        price = i['price']
                        amount = i['amount']
                        sell_list.append([price, amount])
            if 'bids' in res:
                if res['bids'] is not None:
                    for i in res['bids']:
                        price = i['price']
                        amount = i['amount']
                        buy_list.append([price, amount])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {"bids": buy_list, "asks": sell_list}

    async def depth_my(self, symbol):
        path = '/api/v1/Order/active'
        req = {
            "symbol": symbol,
            'timestamp': str(int(time.time() * 1000))
        }
        query, sign = produce_sign(path, self.__secret_key, req)
        h = {
            'X-LA-KEY': self.__api_key,
            'X-LA-SIGNATURE': sign,
            'X-LA-HASHTYPE': 'HMAC-SHA256'
        }
        res = await http_request('GET', self.__base_url + path + query, headers=h)

        if res is False:
            return False

        buy_list = []
        sell_list = []
        if isinstance(res, list):
            for i in res:
                price = float(i['price'])
                amount = float(i['amount'])
                order_id = i['orderId']
                if i['side'] == 'sell':
                    sell_list.append([price, order_id, amount])
                if i['side'] == 'buy':
                    buy_list.append([price, order_id, amount])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {"bids": buy_list, "asks": sell_list}

    async def create_order(self, symbol, price, amount, side):
        path = '/api/v1/Order/new'
        req = {
            'Symbol': symbol,
            'Side': side.lower(),
            'Price': price,
            'Amount': amount,
            'OrderType': 'limit',
            'Timestamp': str(int(time.time() * 1000))
        }
        query, sign = produce_sign(path, self.__secret_key, req)
        h = {
            'X-LA-KEY': self.__api_key,
            'X-LA-SIGNATURE': sign,
            'X-LA-HASHTYPE': 'HMAC-SHA256'
        }
        res = await http_request('POST', self.__base_url + path + query, params=req, headers=h)
        print('order', symbol, price, amount, side, res)

    async def cancel_order(self, order_id):
        path = '/api/v1/Order/cancel'
        req = {

            'timestamp': int(time.time() * 1000),
            'orderId': order_id
        }
        query, sign = produce_sign(path, self.__secret_key, req)
        h = {
            'X-LA-KEY': self.__api_key,
            'X-LA-SIGNATURE': sign,
            'X-LA-HASHTYPE': 'HMAC-SHA256'
        }
        res = await http_request('POST', self.__base_url + path + query, params=req, headers=h)
        print('cancel', order_id, res)


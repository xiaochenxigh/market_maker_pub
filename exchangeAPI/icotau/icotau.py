
import time
import hashlib
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



class Icotau:
    def __init__(self, api_key, secret_key):
        self.__url = 'https://openapi.icotau.top'
        self.__api_key = api_key
        self.__secret_key = secret_key

    def _produce_sign(self, params):
        sign_str = ''
        params['api_key'] = self.__api_key
        params['time'] = str(int(round(time.time() * 1000)))
        for k in sorted(params.keys()):
            sign_str += '{}{}'.format(k, str(params[k]))
        sign_str += self.__secret_key

        return hashlib.md5(sign_str.encode('utf8')).hexdigest()

    async def ticker(self, symbol):
        path = self.__url + '/open/api/get_ticker'
        request = {
            'symbol': symbol
        }
        res = await http_request('GET', path, request)
        if res is False:
            return False

        if isinstance(res, dict):
            if 'data' in res:
                if res['data']:
                    a = float(res['data']['buy'])
                    b = float(res['data']['sell'])
                    return (a, b)

    async def depth_all(self, symbol):
        path = self.__url + '/open/api/market_dept'
        request = {
            'symbol': symbol,  # 币种对
            'type': 'step0'  # 深度类型,step0, step1, step2（合并深度0-2）；step0时，精度最高
        }
        res = await http_request('GET', path, request)
        if not res:
            return False

        buy_list = []
        sell_list = []
        if isinstance(res, dict):
            if 'data' in res:
                if res['data']:
                    if 'tick' in res['data']:
                        if res['data']['tick']:
                            if 'bids' in res['data']['tick']:
                                for i in res['data']['tick']['bids']:
                                    price = float(i[0])
                                    amount = float(i[1])
                                    buy_list.append([price, amount])
                            if 'asks' in res['data']['tick']:
                                for i in res['data']['tick']['asks']:
                                    price = float(i[0])
                                    amount = float(i[1])
                                    sell_list.append([price, amount])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)  # data["data"]["tick"]["bids"]
        sell_list = sorted(sell_list, key=itemgetter(0))  # data["data"]["tick"]["asks"]
        return {'bids': buy_list, 'asks': sell_list}

    async def depth_my(self, symbol):
        path = self.__url + '/exchange-open-api/open/api/v2/new_order'
        request = {
            "pageSize": 200,
            "symbol": symbol
        }
        request['sign'] = self._produce_sign(request)
        res = await http_request('GET', path, request)
        if not res:
            return False

        buy_list = []
        sell_list = []
        if isinstance(res, dict):
            if 'data' in res:
                if res['data']:
                    if 'resultList' in res['data']:
                        if res['data']['resultList']:
                            for i in res['data']['resultList']:
                                price = float(i["price"])
                                amount = float(i["volume"])
                                order_id = i["id"]
                                if i['side'] == "BUY":
                                    buy_list.append((price, order_id, amount))
                                if i['side'] == "SELL":
                                    sell_list.append((price, order_id, amount))
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)  # data["data"]["tick"]["bids"]
        sell_list = sorted(sell_list, key=itemgetter(0))  # data["data"]["tick"]["asks"]
        return {'bids': buy_list, 'asks': sell_list}

    async def balances(self):
        path = self.__url + '/open/api/user/account'
        request = {}
        request['sign'] = self._produce_sign(request)
        res = await http_request('GET', path, request)
        if not res:
            return False
        bal = {}
        if isinstance(res, dict):
            if 'data' in res:
                if res['data']:
                    if 'coin_list' in res['data']:
                        if res['data']['coin_list']:
                            for i in res['data']['coin_list']:
                                free = float(i["normal"])
                                freeze = float(i["locked"])
                                coin = i["coin"]
                                if free + freeze > 0.0:
                                    bal[coin] = {"free": free, "freeze": freeze}
        return bal

    async def create_order(self, symbol, price, amount, side):
        path = self.__url + '/open/api/create_order'
        request = {
            "side": side.upper(),  # buy or sell
            "type": 1,  # 挂单类型:1.限价委托2.市价委托
            "volume": amount,  # type=1买卖数量 type=2买总价格，卖总个数
            "price": price,  # type=1委托单价
            "symbol": symbol,  # 市场标记
            "fee_is_user_exchange_coin": 0
        }
        request['sign'] = self._produce_sign(request)
        res = await http_request('POST', path, request)
        if res['code'] == 0:
            print('order', symbol, price, amount, side, res['code'])
        else:
            print('order', symbol, price, amount, side, res)

    async def cancel_order(self, symbol, order_id):
        path = self.__url + '/open/api/cancel_order'
        request = {
            "order_id": order_id,
            "symbol": symbol
        }
        request['sign'] = self._produce_sign(request)
        res = await http_request('POST', path, request)
        if res['code'] == 0:
            print('order', symbol, order_id, res['code'])
        else:
            print('order', symbol, order_id, res)

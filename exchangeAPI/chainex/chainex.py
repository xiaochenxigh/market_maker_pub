
import time
import hashlib
import random
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

def produce_sign(api_key, secret_key, params):
    params['api_key'] = api_key
    params['time'] = int(time.time())+random.randint(1,100000)
    str_sign = ''
    for i in sorted(params.keys()):
        str_sign += str(params[i])
    str_sign += secret_key
    return hashlib.md5(str_sign.encode('utf-8')).hexdigest()


class Chainex:
    def __init__(self, api_key, secret_key=None):
        self.__url = 'https://www.chainex.in/api'
        self.__api_key = api_key
        self.__secret_key = secret_key

    async def ticker(self, symbol):
        path = self.__url + '/tickers/'
        req = {
            'symbol': symbol,
            'api_key': self.__api_key
        }

        res = await http_request('GET', path, req)
        tickers = {}
        for i in res['data']:
            tickers[i['symbol']] = [float(i['last']), float(i['last'])]
        return tickers

    async def depth_all(self, symbol):
        path = self.__url + '/depth/'
        req = {
            'symbol': symbol,
            'api_key': self.__api_key
        }

        res = await http_request('GET', path, req)
        if not res:
            return False
        buy_list = []
        sell_list = []
        if isinstance(res, dict):
            if 'data' in res:
                if isinstance(res['data'], dict):
                    if 'asks' in res['data']:
                        if isinstance(res['data']['asks'], list):
                            for i in res['data']['asks']:
                                price = float(i[0])
                                amount = float(i[1])
                                sell_list.append([price, amount])
                    if 'bids' in res['data']:
                        if isinstance(res['data']['bids'], list):
                            for i in res['data']['bids']:
                                price = float(i[0])
                                amount = float(i[1])
                                buy_list.append([price, amount])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {'asks': sell_list, 'bids': buy_list}

    async def depth_my(self, symbol):
        path = self.__url + '/order_list/'
        req = {
            'symbol': symbol,
            'page': 1,
            'api_key': self.__api_key
        }
        sign = produce_sign(self.__api_key, self.__secret_key, req)
        h = {'Sign': sign}
        res = await http_request('POST', path, req, headers=h)
        if not res:
            return False
        buy_list = []
        sell_list = []
        for i in res['data']:
            price = float(i['price'])
            amount = float(i['amount'])
            order_id = i['order_id']
            if i['type']=='sell':
                sell_list.append([price,order_id,amount])
            if i['type']=='buy':
                buy_list.append([price,order_id,amount])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {'asks': sell_list, 'bids': buy_list}

    async def balances(self):
        path = self.__url + '/user_info'
        req = {
        }
        sign = produce_sign(self.__api_key, self.__secret_key, req)
        h = {'Sign': sign}
        res = await http_request('POST', path, req, headers=h)
        if not res:
            return False
        bal = {}
        if 'data' in res:
            if res['data']:
                free_dict = res['data']['free']
                freeze_dict = res['data']['freezed']
                for i in free_dict:
                    free = float(free_dict[i])
                    freeze = float(freeze_dict[i])
                    if free+freeze>0:
                        bal[i]={'free':free,'freeze':freeze}
        return bal

    async def create_order(self, symbol, price, amount, side):
        """
        :param symbol:
        :param price:
        :param amount:
        :param side: 1 buy,2 sell
        :return:
        """
        path = self.__url + '/trade/'
        req = {
            'symbol': symbol,
            'type': side,
            'price': price,
            'amount': amount,
            'api_key': self.__api_key
        }
        sign = produce_sign(self.__api_key, self.__secret_key, req)
        h = {'Sign': sign}
        res = await http_request('POST', path, req, headers=h)
        print(res)

    async def cancel_order(self, order_id):
        path = self.__url + '/cancel_order/'
        req = {
            'id': order_id,
            'api_key': self.__api_key
        }
        h = {'Sign': produce_sign(self.__api_key, self.__secret_key, req)}
        res = await http_request('POST', path, req, headers=h)


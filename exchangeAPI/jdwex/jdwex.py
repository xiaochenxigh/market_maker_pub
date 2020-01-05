import hashlib
from operator import itemgetter
import aiohttp
import json
import logging
import urllib


def produce_sign(api_key, secret_key, params):
    params['api_key'] = api_key
    sign_str = ''
    for k in sorted(params.keys()):
        if sign_str:
            sign_str += '&'
        sign_str += '{}={}'.format(k, params[k])
    sign_str += '&secret_key={}'.format(secret_key)
    return hashlib.md5(sign_str.encode("utf8")).hexdigest().upper()

async def http_request(method, url, params=None, headers=None,auth=None):
    try:
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(auth=auth,connector=conn) as session:
            if method == "POST":
                async with session.post(url, data=params, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        response = await response.read()
                        return json.loads(response)
                    else:
                        logging.error('{}'.format(await response.read()))
    except Exception as e:
       logging.error('{}_{}_{}'.format(url, params, e))
    return False


class Jdwex:
    def __init__(self, api_key, secret_key):
        self.__api_key = api_key
        self.__secret_key = secret_key
        self.__url = 'https://www.jdwex.com'

    async def all_symbol(self):
        path = self.__url + '/appApi.html?action=mappings'
        res = await http_request('POST', path)
        print(res)

    async def depth_all(self, symbol):
        path = self.__url + '/appApi.html?action=depth'
        req = {
            'symbol': int(symbol),
            'size': 1
        }
        # req['sign'] = produce_sign(self.__api_key,self.__secret_key,req)
        res = await http_request('POST', path, params=req)
        if not res:
            return False

        buy_list = []
        sell_list = []
        if isinstance(res, dict):
            if 'data' in res:
                if res['data']:
                    if 'bids' in res['data']:
                        for i in res['data']['bids']:
                            price = float(i[0])
                            amount = float(i[1])
                            buy_list.append([price, amount])
                    if 'asks' in res['data']:
                        for i in res['data']['asks']:
                            price = float(i[0])
                            amount = float(i[1])
                            sell_list.append([price, amount])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {"bids": buy_list, "asks": sell_list}

    async def depth_my(self, symbol):
        path = self.__url + '/appApi.html?action=entrust'
        req = {
            'symbol': int(symbol)
        }
        req['sign'] = produce_sign(self.__api_key, self.__secret_key, req)
        res = await http_request('POST', path, params=req)
        if not res:
            return False

        buy_list = []
        sell_list = []
        if isinstance(res, dict):
            if 'data' in res:
                if res['data']:
                    for i in res['data']:
                        price = float(i['price'])
                        amount = float(i['amount'])
                        order_id = i['id']
                        if i['type'] == 1:
                            sell_list.append([price, order_id, amount])
                        if i['type'] == 0:
                            buy_list.append([price, order_id, amount])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {"bids": buy_list, "asks": sell_list}

    async def balances(self):
        path = self.__url + '/appApi.html?action=userinfo'
        req = {}
        req['sign'] = produce_sign(self.__api_key, self.__secret_key, req)
        res = await http_request('POST', path, params=req)
        if not res:
            return False

        bal = {}
        if isinstance(res, dict):
            if 'data' in res:
                if res['data']:
                    if 'free' in res['data']:
                        if res['data']['free']:
                            for coin in res['data']['free']:
                                free = res['data']['free'][coin]
                                freeze = res['data']['frozen'][coin]
                                if free + freeze > 0:
                                    bal[coin] = {'free': free, 'freeze': freeze}
        return bal

    async def create_order(self, symbol, price, amount, side):
        path = self.__url + '/appApi.html?action=trade'
        req = {
            'symbol': symbol,
            'type': side,
            'amount': amount,
            'price': price
        }
        req['sign'] = produce_sign(self.__api_key, self.__secret_key, req)
        res = await http_request('POST', path, params=req)
        if not res:
            return False
        print('order', symbol, price, amount, side, res)

    async def cancel_order(self, order_id):
        path = self.__url + '/appApi.html?action=cancel_entrust'
        req = {
            'id': order_id
        }
        req['sign'] = produce_sign(self.__api_key, self.__secret_key, req)
        res = await http_request('POST', path, params=req)
        print('cancel', order_id, res)

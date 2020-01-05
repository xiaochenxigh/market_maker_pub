
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


def produce_sign(api_key, secret_key, params):
    strx = ''
    params['api_key'] = api_key
    for i in sorted(params.keys()):
        strx += ('%s=%s' % (i, str(params[i])))
        strx += '&'
    sign_str = strx + 'secret_key=' + secret_key
    return hashlib.md5(sign_str.encode("utf8")).hexdigest().upper()


class Zt():
    def __init__(self, api_key, secret_key):
        self.__api_key = api_key
        self.__secret_key = secret_key

    async def depth_all(self, symbol):
        path = 'https://www.zt.com/api/v1/depth'
        req = {
            "symbol": symbol,
            "size": 100
        }
        h = {'X-SITE-ID': 1}
        res = await http_request("GET", path, req, h)
        if not res:
            return False

        buy_list = []
        sell_list = []
        if 'asks' in res:
            for i in res['asks']:
                sell_list.append([float(i[0]), float(i[1])])
        if 'bids' in res:
            for i in res['bids']:
                buy_list.append([float(i[0]), float(i[1])])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {"bids": buy_list, "asks": sell_list}

    async def depth_my(self, symbol):
        path = 'https://www.zt.com/api/v1/private/order/pending'
        req = {
            "market": symbol,
            "offset": 1,
            "limit": 100
        }
        req['sign'] = produce_sign(self.__api_key, self.__secret_key, req)
        h = {'X-SITE-ID': '1'}
        res = await http_request("POST", path, req, h)

        if not res:
            return False

        buy_list = []
        sell_list = []
        if 'result' in res:
            if 'records' in res['result']:
                if not res['result']['records']:
                    return False
                for i in res['result']['records']:
                    price = float(i['price'])
                    amount = float(i['left'])
                    order_id = i['id']
                    if i['side'] == 1:
                        sell_list.append([price, order_id, amount])
                    if i['side'] == 2:
                        buy_list.append([price, order_id, amount])
        sell_list = sorted(sell_list, key=itemgetter(0))
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)

        return {'bids': buy_list, 'asks': sell_list}

    async def balances(self):
        path = 'https://www.zt.com/api/v1/private/user'
        req = {}
        req['sign'] = produce_sign(self.__api_key, self.__secret_key, req)
        h = {'X-SITE-ID': '1'}
        res = await http_request("POST", path, req, h)

        if not res:
            return False

        bal = {}
        if 'result' in res:
            for i in res['result']:
                if i != 'user_id':
                    free = float(res['result'][i]['available'])
                    freeze = float(res['result'][i]['freeze'])
                    if free + freeze > 0:
                        bal[i] = {"free": free, "freeze": freeze}
        return bal

    async def create_order(self, symbol, price, amount, side):
        """
        1:sell
        2:buy
        """
        path = 'https://www.zt.com/api/v1/private/trade/limit'
        req = {
            "market": symbol,
            "price": price,
            "amount": amount,
            "side": side
        }
        req['sign'] = produce_sign(self.__api_key, self.__secret_key, req)
        h = {'X-SITE-ID': '1'}
        res = await http_request("POST", path, req, h)
        print(req, res)

    async def cancel_order(self, symbol, order_id):
        path = 'https://www.zt.com/api/v1/private/trade/cancel'
        req = {
            "market": symbol,
            "order_id": order_id
        }
        req['sign'] = produce_sign(self.__api_key, self.__secret_key, req)
        h = {'X-SITE-ID': '1'}
        res = await http_request("POST", path, req, h)
        print(req, res['code'])


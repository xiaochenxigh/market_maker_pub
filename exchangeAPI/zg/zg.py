import sys,os;sys.path.append(os.path.abspath(os.path.dirname(__file__)  +  '/' + '../'))#;print(sys.path)
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


def produce_sign(api_key, secret_key, params={}):
    strx = ''
    params['api_key'] = api_key
    #params['time'] = int(time.time()*1000)
    for i in sorted(params.keys()):
        strx += ('%s=%s' % (i, str(params[i])))
        strx += '&'
    sign_str = strx+'secret_key='+secret_key
    return hashlib.md5(sign_str.encode("utf8")).hexdigest().upper()


class Zgcom():
    def __init__(self, api_key, secret_key):
        self.__api_key = api_key
        self.__secret_key = secret_key

    @staticmethod
    async def depth_all(symbol):
        path = "https://api1.zg.com/depth"
        req = {
            "symbol": symbol,
            "size": 100
        }
        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
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
        path = 'https://api1.zg.com/private/order/pending'
        req = {
            'market': symbol,
            "offset": 0,
            'limit': 200
        }
        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        req['sign'] = produce_sign(self.__api_key, self.__secret_key, req)
        res = await http_request("POST", path, req, h)

        if not res:
            return False

        buy_list = []
        sell_list = []
        if 'result' in res:
            if 'records' in res['result']:
                if not res['result']['records']:
                    return {"bids": buy_list, "asks": sell_list}
                for i in res['result']['records']:
                    symbol = i['market']
                    price = float(i['price'])
                    amount = float(i['amount'])
                    order_id = i['id']
                    if i['type'] == 2:
                        buy_list.append([price, order_id, amount])
                    if i['type'] == 1:
                        sell_list.append([price, order_id, amount])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {"bids": buy_list, "asks": sell_list}

    async def balances(self):
        path = 'https://api1.zg.com/private/user'
        req = {}
        req['sign'] = produce_sign(self.__api_key, self.__secret_key, req)
        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        res = await http_request("POST", path, req, h)
        if not res:
            return False

        bal = {}
        if 'result' in res:
            for i in res['result']:
                bal[i] = {"free": res['result'][i]['available'],
                          "freeze": res['result'][i]['freeze']}
        return bal

    async def create_order(self, symbol, price, amount, side):
        """ 1 sell
            2 buy"""
        path = 'https://api1.zg.com/private/trade/limit'
        req = {
            "market": symbol,
            "price": price,
            "amount": amount,
            "side": side
        }
        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        req['sign'] = produce_sign(self.__api_key, self.__secret_key, req)
        res = await http_request("POST", path, req, h)
        print(req, res)

    async def cancel_order(self, symbol, order_id):
        path = 'https://api1.zg.com/private/trade/cancel'
        req = {
            "market": symbol,
            'order_id': order_id
        }
        req['sign'] = produce_sign(self.__api_key, self.__secret_key, req)
        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        res = await http_request("POST", path, req, h)
        print(req, res)



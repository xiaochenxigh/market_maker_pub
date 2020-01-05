
import hashlib
import json
import aiohttp
import time
from operator import itemgetter

def produce_sign(apikey, secretkey, params={}):
    strx = ''
    params['apikey'] = apikey
    params['time'] = int(time.time()*1000)
    for i in sorted(params.keys()):
        strx +=('%s=%s' % (i, str(params[i])))
        strx += '&'
    sign_str = strx+'secret_key='+secretkey
    return hashlib.md5(sign_str.encode("utf8")).hexdigest().upper()


async def http_request(method, url, params, headers=None):
    async with aiohttp.ClientSession() as session:
        if method == "GET":
            async with session.get(url, params=params, timeout=2.5) as response:
                response = await response.read()
                return json.loads(response)
        if method == "POST":
            async with session.post(url, data=params, headers=headers, timeout=2.5) as response:
                response = await response.read()
                return json.loads(response)


class Coinbig():
    def __init__(self, apikey, secretkey):
        self.__apikey = apikey
        self.__secretkey = secretkey

    @staticmethod
    async def depth_all(symbol):
        path = "https://www.coinbig.com/api/publics/vip/depth"
        req = {
            "symbol": symbol,
            "size": 100
        }
        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        res = await http_request("GET", path, req)
        if not res:
            return False
        #print(res)
        buy_list = []
        sell_list = []
        if 'data' in res:
            if not res['data']:
                return {"bids":buy_list,"asks":sell_list}
            if 'asks' in res['data']:
                sell_list = res['data']['asks']
            if 'bids' in res['data']:
                buy_list = res['data']['bids']

        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {"bids": buy_list, "asks": sell_list}

    async def depth_my(self, symbol):
        path = 'https://www.coinbig.com/api/publics/vip/orders_info'
        req = {
            'symbol': symbol,
            "size": 50,
            'type': '1,2'
        }
        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        req['sign'] = produce_sign(self.__apikey, self.__secretkey, req)
        res = await http_request("POST", path, req, h)
        if not res:
            return False

        buy_list = []
        sell_list = []
        if 'data' in res:
            if not res['data']:
                return {"bids":buy_list,"asks":sell_list}
            if 'orders' in res['data']:
                for i in res['data']['orders']:
                    price = float(i['price'])
                    amount = float(i['leftCount'])
                    order_id = i['order_id']
                    if i['entrustType'] == 0:
                        buy_list.append([price, order_id, amount])
                    if i['entrustType'] == 1:
                        sell_list.append([price, order_id, amount])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {"bids": buy_list, "asks": sell_list}

    async def balances(self):
        path = 'https://www.coinbig.com/api/publics/vip/userinfo'
        req = {
        }
        req['sign'] = produce_sign(self.__apikey, self.__secretkey, req)
        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        res = await http_request("POST", path, req, h)
        if not res:
            return False
        bal = {}
        if 'data' in res:
            if 'info' in res['data']:
                list1 = res['data']['info']['free']
                list2 = res['data']['info']['freezed']
                for i in list1:
                    if list1[i] > 0:
                        bal[i] = {"free": list1[i], "freeze": list2[i]}
        return bal

    async def create_order(self, symbol, price, amount, side):
        """
        sell
        buy
        """
        path = 'https://www.coinbig.com/api/publics/vip/trade'
        req = {
            "symbol": symbol,
            "price": price,
            "amount": amount,
            "type": side
        }
        req['sign'] = produce_sign(self.__apikey, self.__secretkey, req)
        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        res = await http_request("POST", path, req, h)
        print("ORDER",symbol,price,amount,side, res)

    async def cancel_order(self, order_id):
        path = 'https://www.coinbig.com/api/publics/vip/cancel_order'
        req = {
            'order_id': order_id
        }
        req['sign'] = produce_sign(self.__apikey, self.__secretkey, req)
        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        res = await http_request("POST", path, req, h)
        print(req, res)


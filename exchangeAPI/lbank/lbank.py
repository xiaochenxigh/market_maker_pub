# --*-- coding:utf-8 --*--
from hashlib import md5
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode
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


class Lbank:
    def __init__(self, api_key, private_key):
        self.__base_url = "https://api.lbkex.com/"
        self.__api_key = api_key
        if private_key:
            if len(private_key) > 32:
                if private_key.split('\n')[0] == '-----BEGIN RSA PRIVATE KEY-----':
                    pass
                else:
                    private_key = '\n'.join([
                        '-----BEGIN RSA PRIVATE KEY-----',
                        private_key,
                        '-----END RSA PRIVATE KEY-----'
                    ])

                private_key = RSA.importKey(private_key)
                self._signer = PKCS1_v1_5.new(private_key)
            else:
                self._signer = None
                self._private_key = private_key
        else:
            self._signer = self._private_key = None

    def build_sign(self, parms):
        if self._signer:
            parms = ['%s=%s' % i for i in sorted(parms.items())]
            parms = '&'.join(parms).encode('utf-8')
            message = md5(parms).hexdigest().upper()

            digest = SHA256.new()
            digest.update(message.encode('utf-8'))
            signature = b64encode(self._signer.sign(digest))
        elif self._private_key:
            parms = ['%s=%s' % i for i in sorted(parms.items())]
            parms = '&'.join(parms) + '&secret_key=' + self._private_key
            signature = md5(parms.encode('utf-8')).hexdigest().upper()
        else:
            return False

        return signature.decode('utf-8')

    async def depth_all(self, symbol):
        path = 'https://www.lbkex.net/v1/depth.do'
        req = {
            "symbol": symbol,
            "size": "10",
            "merge": "0"
        }

        header = {'contentType': 'application/x-www-form-urlencoded'}
        res = await http_request('GET', path, req, header)
        return res

    async def depth_my(self, symbol):
        path = "https://www.lbkex.net/v1/orders_info_no_deal.do"
        req = {
            "api_key": self.__api_key,
            "symbol": symbol,
            "current_page": "1",
            "page_length": "100"
        }
        req["sign"] = self.build_sign(req)
        header = {'contentType': 'application/x-www-form-urlencoded'}
        res = await http_request('POST', path, req, header)
        buy_list = []
        sell_list = []
        data = res["orders"]
        for i in data:
            price = float(i["price"])
            amount = float(i["amount"])
            order_id = i["order_id"]
            if i["type"] == "sell":
                sell_list.append([price, order_id, amount])
            if i["type"] == "buy":
                buy_list.append([price, order_id, amount])

        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {"bids": buy_list, "asks": sell_list}

    async def create_order(self, symbol, price, amount, side):
        path = "https://www.lbkex.net/v1/create_order.do"
        req = {
            "api_key": self.__api_key,
            "symbol": symbol,
            "type": side.lower(),
            "price": price,
            "amount": amount
        }
        req["sign"] = self.build_sign(req)
        header = {'contentType': 'application/x-www-form-urlencoded'}
        res = await http_request('POST', path, req, header)
        print('order', symbol, price, amount, side, res)

    async def balances(self):
        path = 'https://www.lbkex.net/v1/user_info.do'
        req = {
            "api_key": self.__api_key
        }
        req["sign"] = self.build_sign(req)
        header = {'contentType': 'application/x-www-form-urlencoded'}
        res = await http_request('POST', path, req, header)
        if not res:
            return False

        bal = {}
        if 'info' in res:
            for i in res['info']['free']:
                free = float(res['info']['free'][i])
                freeze = float(res['info']['freeze'][i])
                if free + freeze > 0:
                    bal[i] = {'free': free, 'freeze': freeze}
        return bal

    async def cancel_order(self, symbol, order_id):
        path = "https://www.lbkex.net/v1/cancel_order.do"
        req = {
            "api_key": self.__api_key,
            "symbol": symbol,
            "order_id": order_id
        }
        req["sign"] = self.build_sign(req)
        header = {'contentType': 'application/x-www-form-urlencoded'}
        res = await http_request('POST', path, req, header)
        print('cancel', symbol, order_id)


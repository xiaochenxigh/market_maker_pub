# encoding=utf-8
import hmac
import hashlib
import base64
import json
import time
import aiohttp
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


class FubtApi:
    def __init__(self, apikey, secretkey, pay_password=None):
        self.apikey = apikey
        self.secretkey = secretkey
        self.payPwd = pay_password
        self.api_url = 'https://api.fubt.co/v1'

    def get_sign(self, params):
        keys = sorted(params.keys())
        s = '&'.join(['%s=%s' % (k, params[k]) for k in keys])
        print(s)
        h = hmac.new(self.secretkey.encode(
            'utf-8'), s.encode('utf-8'), hashlib.sha256)
        return base64.b64encode(h.digest())

    async def fetch_ticker(self, symbol):
        endpoint = '/market/ticker'
        params = {
            "symbol": self.clean(symbol),
            "accessKey": self.apikey
        }

        res = await http_request('GET', self.api_url + endpoint, params)
        if not res:
            return False

    async def depth_all(self, symbol):
        endpoint = '/market/depth'
        params = {
            "symbol": self.clean(symbol),
            "step": 'STEP0',
            "accessKey": self.apikey
        }

        res = await http_request('GET', self.api_url + endpoint, params)

        buy_list = []
        sell_list = []
        if 'data' in res:
            if not res['data']:
                return {"bids": buy_list, "asks": sell_list}
            if 'buy' in res['data']:
                for i in res['data']['buy']:
                    buy_list.append([float(i['price']), float(i['amount'])])
            if 'sell' in res['data']:
                for i in res['data']['sell']:
                    sell_list.append([float(i['price']), float(i['amount'])])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        return {"bids": buy_list, "asks": sell_list}

    async def create_order(self, symbol, price, amount, side):
        endpoint = '/order/saveEntrust'
        params = {
            "count": amount,
            "matchType": "LIMIT",
            "payPwd": self.payPwd,
            "price": price,
            "symbol": self.clean(symbol),
            "type": side.upper(),
            "accessKey": self.apikey,
            "timestamp": int(time.time() * 1000)
        }
        params['signature'] = self.get_sign(params).decode('utf-8')
        h = {
            "content-type": "application/json;charset=UTF-8"
        }
        res = await http_request('POST', self.api_url + endpoint, params, headers=h)
        print(params, res)

    async def balances(self):
        endpoint = '/personal/getUserFinanceList'
        params = {
            "selectType": "noall",
            "accessKey": self.apikey
        }

        res = await http_request('GET', self.api_url + endpoint, params)
        if not res:
            return False
        bal = {}
        if 'data' in res:
            for i in res['data']:
                coin = i['coinName']
                free = float(i['total'])
                freeze = float(i['frozen'])
                bal[coin] = {"free": free, "freeze": freeze}
        return bal

    def clean(self, symbol):
        return symbol.replace('/', '').lower()

    async def depth_my(self, symbol):
        endpoint = '/order/openOrders'
        params = {
            "symbol": self.clean(symbol),
            "accessKey": self.apikey
        }

        res = await http_request('GET', self.api_url + endpoint, params)

        if not res:
            return False

        buy_list = []
        sell_list = []

        if 'data' in res:
            if 'list' in res['data']:
                for i in res['data']['list']:
                    price = float(i['price'])
                    amount = float(i['leftCount'])
                    order_id = i['id']
                    if i['type'] == "BUY":
                        buy_list.append([price, order_id, amount])
                    if i['type'] == "SELL":
                        sell_list.append([price, order_id, amount])

        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)  # data["data"]["tick"]["bids"]
        sell_list = sorted(sell_list, key=itemgetter(0))  # data["data"]["tick"]["asks"]
        return {"bids": buy_list, "asks": sell_list}

    async def cancel_order(self, order_id):
        endpoint = '/order/cancelEntrust'
        params = {
            "id": order_id,
            "accessKey": self.apikey,
            "timestamp": int(time.time() * 1000)
        }
        params['signature'] = self.get_sign(params).decode('utf-8')
        headers = {
            "content-type": "application/json;charset=UTF-8"
        }
        res = await http_request('POST', self.api_url + endpoint, params, headers=headers)
        print(params, res)


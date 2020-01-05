import base64
import hashlib
import hmac
import urllib
import urllib.parse
import urllib.request
import time
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


def produce_sign(method, base_url, path, params, api_key, secret_key):
    utc_time = int(time.time())
    params_to_sign = {'AccessKeyId': api_key,
                      'SignatureMethod': 'HmacSHA256',
                      'SignatureVersion': '2',
                      'Timestamp': utc_time,
                      }
    params.update(params_to_sign)

    tempParams = urllib.parse.urlencode(sorted(params.items(), key=lambda d: d[0], reverse=False))

    payload = "\n".join([method, base_url, path, tempParams]).encode(encoding="UTF-8")

    return str(
        base64.b64encode(hmac.new(secret_key.encode(encoding='UTF-8'), payload, digestmod=hashlib.sha256).digest()),
        encoding="utf-8")


class Hotcoin:
    def __init__(self, api_key, secret_key):
        self.url = "hkapi.hotcoin.top"
        self.apikey = api_key
        self.secretkey = secret_key

    async def depth_all(self, symbol):
        path = "/v1/depth"
        req = {
            "symbol": symbol,
            "step": 60
        }
        req["Signature"] = produce_sign("POST", self.url, path, req, self.apikey, self.secretkey)
        res = await http_request('POST', "https://" + self.url + path, req)
        buy_list = []
        sell_list = []
        if "data" in res:
            if res['data']:
                if "depth" in res["data"]:
                    if "asks" in res["data"]["depth"]:
                        sell_list = res["data"]["depth"]["asks"]
                    if "bids" in res["data"]["depth"]:
                        buy_list = res["data"]["depth"]["bids"]

        return {"bids": buy_list, "asks": sell_list}

    # open_orders
    async def depth_my(self, symbol):
        path = "/v1/order/entrust"
        req = {
            "symbol": symbol,
            "type": 1,
            "count": 100
        }
        req["Signature"] = produce_sign("POST", self.url, path, req, self.apikey, self.secretkey)
        res = await http_request('POST', "https://" + self.url + path, req)
        buy_list = []
        sell_list = []
        if "data" in res:
            if res['data']:
                if "entrutsCur" in res["data"]:
                    for i in res["data"]["entrutsCur"]:
                        price = i["price"]
                        amount = i["leftcount"]
                        order_id = i["id"]
                        if i["type"] == 0:
                            buy_list.append([price, order_id, amount])
                        if i["type"] == 1:
                            sell_list.append([price, order_id, amount])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)  # data["data"]["tick"]["bids"]
        sell_list = sorted(sell_list, key=itemgetter(0))  # data["data"]["tick"]["asks"]
        return {"bids": buy_list, "asks": sell_list}

    # create_order
    async def create_order(self, symbol, price, amount, side):
        path = "/v1/order/place"
        req = {
            "symbol": symbol,
            "type": side,
            "tradePrice": str(price),
            "tradeAmount": str(amount)
        }
        req["Signature"] = produce_sign("POST", self.url, path, req, self.apikey, self.secretkey)
        res = await http_request('POST', "https://" + self.url + path, req)
        print('order', symbol, price, amount, side, res)
        return req, res

    # cancel_order
    async def cancel_order(self, order_id):
        path = "/v1/order/cancel"
        req = {
            "id": order_id
        }
        req["Signature"] = produce_sign("POST", self.url, path, req, self.apikey, self.secretkey)
        res = await http_request('POST', "https://" + self.url + path, req)
        print(req, res)
        return req, res

    async def balances(self):
        path = "/v1/balance"
        req = {
        }
        req["Signature"] = produce_sign("POST", self.url, path, req, self.apikey, self.secretkey)
        res = await http_request('POST', "https://" + self.url + path, req)

        balances = {}
        if "data" in res:
            if "wallet" in res["data"]:
                for i in res["data"]["wallet"]:
                    symbol = i["shortName"]
                    free = i["total"]
                    freeze = i["frozen"]
                    if free + freeze > 0.0:
                        balances[symbol] = {"free": free, "freeze": freeze}
        return balances


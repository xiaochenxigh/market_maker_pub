# --*-- coding:utf-8 --*--

import asyncio
import aiohttp
import json
import time
import hashlib
from operator import itemgetter
from websocket import create_connection


def process_sign(method, api_key, secret_key, api_url, **payload):
    timestamp = str(int(time.time() * 1000))

    param = ''
    if method == 'GET' and payload:
        for k in sorted(payload):
            param += k + str(payload[k])
    elif method == 'POST' and payload:
        # param = json.dumps(payload, separators=(',', ':'))
        param = json.dumps(payload)
    elif not payload:
        payload = ''

    sig_str = api_key + timestamp + param + secret_key
    # print(sig_str)
    signature = hashlib.md5(sig_str.encode('utf-8')).hexdigest()
    # print(sig_str,signature)
    headers = {
        'Apiid': api_key,
        'Timestamp': timestamp,
        'Sign': signature
    }
    return headers, payload


async def get_http(url, params, headers):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=2.5) as response:
                response = await response.read()
                return json.loads(response)
    except:
        return False


async def post_http(url, params, headers):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, headers=headers, timeout=2.5) as response:
                response = await response.read()
                return json.loads(response)
    except:
        return False


class Bw:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    async def get_market_id(self, market_id):
        path = 'https://www.bw.io/exchange/config/controller/website/marketcontroller/getByWebId'
        res = await get_http(path, {}, {})
        if not res:
            return False
        x = {}
        if 'datas' in res:
            for i in res['datas']:
                if i["marketId"] == str(market_id):
                    return i['name']  # .upper()

    async def depth_all_ws(self, market_id):
        ws = create_connection("wss://kline.bw.io/websocket")
        symbol = await self.get_market_id(market_id)

        ws.send(
            json.dumps({"dataType": "{}_ENTRUST_ADD_{}".format(market_id, symbol), "dataSize": 50, "action": "ADD"}))
        result = ws.recv()
        data = json.loads(result)
        buy_list = []
        for i in data[0][5]["bids"]:
            price = float(i[0])
            amount = float(i[1])
            buy_list.append([price, amount])

        sell_list = []
        for i in data[0][4]["asks"]:
            price = float(i[0])
            amount = float(i[1])
            sell_list.append([price, amount])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)
        sell_list = sorted(sell_list, key=itemgetter(0))
        ws.close()
        await asyncio.sleep(0.1)
        return {"bids": buy_list, "asks": sell_list}  # """

    async def depth_my(self, market_id):
        path = "https://www.bw.io/exchange/entrust/controller/website/EntrustController/getUserEntrustRecordFromCacheWithPage"
        params = {
            "marketId": market_id,
            "pageSize": 200,
            "pageIndex": 1
        }
        headers, payload = process_sign("GET", self.api_key, self.secret_key, path, **params)

        res = await get_http(path, payload, headers)
        ask_list = []
        bid_list = []

        if not res:
            return {"asks": ask_list, "bids": bid_list}
        if "datas" in res:
            if 'entrustList' in res['datas']:
                for i in res["datas"]['entrustList']:
                    price = float(i["price"])
                    order_id = i["entrustId"]
                    amount = float(i["amount"])
                    trade_type = i["type"]
                    if trade_type == 0:
                        ask_list.append([price, order_id, amount])
                    elif trade_type == 1:
                        bid_list.append([price, order_id, amount])
                    else:
                        pass
        if ask_list:
            ask_list = sorted(ask_list, key=itemgetter(0))
        if bid_list:
            bid_list = sorted(bid_list, key=itemgetter(0), reverse=True)

        depth_temp = {
            "asks": ask_list,
            "bids": bid_list
        }

        return depth_temp

    async def balances(self):
        path = "https://www.bw.io/exchange/fund/controller/website/fundcontroller/findbypage"
        params = {
            "pageSize": 999,
            "pageNum": 0
        }
        headers, payload = process_sign("POST", self.api_key, self.secret_key, path, **params)
        res = await post_http(path, payload, headers)
        if not res:
            return False
        bal = {}
        if 'datas' in res:
            if 'list' in res['datas']:
                for i in res['datas']['list']:
                    coin = i['currencyTypeId']
                    free = float(i['amount'])
                    freeze = float(i['freeze'])
                    bal[coin] = {"free": free, "freeze": freeze}
        return bal

    async def create_order(self, market_id, price, amount, trade_type):
        """
        1,buy
        0,sell
        """
        path = "https://www.bw.io/exchange/entrust/controller/website/EntrustController/addEntrust"
        params = {
            "amount": amount,
            "rangeType": 0,
            "type": trade_type,
            "marketId": market_id,
            "price": price
        }
        headers, payload = process_sign("POST", self.api_key, self.secret_key, path, **params)
        res = await post_http(path, payload, headers)
        print(market_id, price, amount, trade_type, res)
        return res

    async def cancel_order(self, market_id, order_id):
        path = "https://www.bw.io/exchange/entrust/controller/website/EntrustController/cancelEntrust"
        params = {
            "entrustId": order_id,
            "marketId": market_id
        }
        headers, payload = process_sign("POST", self.api_key, self.secret_key, path, **params)
        res = await post_http(path, payload, headers)
        print(res)

    async def cancel_remain(self, market_id, remain_size):
        data = await self.depth_my(market_id)
        if data:
            ask_list = data["asks"]
            bid_list = data["bids"]
            if ask_list:
                for i in range(len(ask_list)):
                    if i < len(ask_list) - remain_size:
                        order_id = ask_list[i][1]
                        print(order_id)
                        await self.cancel_order(market_id, order_id)
            if bid_list:
                for i in range(len(bid_list)):
                    if i < len(bid_list) - remain_size:
                        order_id = bid_list[i][1]
                        await self.cancel_order(market_id, order_id)


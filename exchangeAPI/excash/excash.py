# --*-- coding:utf-8 --*--

import time
import asyncio
import aiohttp
import json
import hashlib
import urllib
from operator import itemgetter
from ExchangeApi.http_utils import http_request


class Excash:
    def __init__(self, api_key, secret_key):
        self.__url = 'https://api.ex.cash'
        self.__apikey = api_key
        self.__secretkey = secret_key

    async def __get_http(self, resource,params):
        url = self.__url + resource
        return await http_request('GET',url,params=params)

    async def __post_http(self, resource, params):
        url = self.__url + resource
        #data = urllib.parse.urlencode(params)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return await http_request('POST',url,params=params,headers=headers)

    def __buildMySign(self, params):
        sign = ''
        for key in sorted(params.keys()):
            sign += key + '=' + str(params[key]) + '&'
        data = sign + 'secret_key=' + self.__secretkey
        return hashlib.md5(data.encode("utf8")).hexdigest().upper()

    async def depth_all(self, symbol, size=100):
        DEPTH_RESOURCE = "/api/depth"
        req = {
            "symbol": symbol,
            "size": size
        }
        temp = await self.__get_http(DEPTH_RESOURCE, req)
        if not temp:
            return False

        buy_list = []
        sell_list = []
        if 'asks' in temp:
            te = json.loads(temp['asks'])
            for i in te:
                price = i[0]
                amount = i[1]
                sell_list.append([price,amount])
        if 'bids' in temp:
            te = json.loads(temp['bids'])
            for i in te:
                price = i[0]
                amount = i[1]
                buy_list.append([price,amount])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)  # data["data"]["tick"]["bids"]
        sell_list = sorted(sell_list, key=itemgetter(0))  # data["data"]["tick"]["asks"]
        return {'bids': buy_list, 'asks': sell_list}

    async def balance(self, coin=""):
        USERINFO_RESOURCE = "/api/userinfo"
        req = {}
        req['api_key'] = self.__apikey
        if coin:
            req['coin'] = coin
        req['sign'] = self.__buildMySign(req)
        temp =  await self.__post_http(USERINFO_RESOURCE, req)
        if not temp:
            return False
        return temp


    async def depth_my(self, symbol):
        RESOURCE = "/api/orders_info_by_status"
        params = {}
        params['api_key'] = self.__apikey
        params['symbol'] = symbol
        params['status'] = 0
        params['sign'] = self.__buildMySign(params)
        print(params)
        temp =  await self.__post_http(RESOURCE, params)
        if not temp:
            return False

        buy_list = []
        sell_list = []
        if 'orders' in temp:
            if temp['orders']:
                for i in temp['orders']:
                    price = float(i['price'])
                    amount = float(i['amount'])
                    order_id = i['order_id']
                    if i['type']=='1':
                        buy_list.append([price,order_id,amount])
                    if i['type']=='2':
                        sell_list.append([price,order_id,amount])
        buy_list = sorted(buy_list, key=itemgetter(0), reverse=True)  # data["data"]["tick"]["bids"]
        sell_list = sorted(sell_list, key=itemgetter(0))  # data["data"]["tick"]["asks"]
        return {'bids': buy_list, 'asks': sell_list}



    async def create_order(self, symbol, tradeType, price, amount, fee=0):
        RESOURCE = "/api/trade"
        params = {
            "symbol": symbol,
            "api_key": self.__apikey,
            "price": price,
            "amount": amount,
            "tradeType": tradeType,
            "fee": fee
        }
        params['sign'] = self.__buildMySign(params)
        return await self.__post_http(RESOURCE, params)

    async def cancel(self, order_id):
        RESOURCE = "/api/cancel_order"
        if order_id:
            params = {
                "api_key": self.__apikey,
                "order_id": order_id
            }
            params['sign'] = self.__buildMySign(params)
            return await self.__post_http(RESOURCE, params)
        else:
            return "no_cancel_order"

    async def cancel_remain(self, symbol, remain_size):
        open_orders = await self.depth_my(symbol)
        order_id_list = ""
        askList = open_orders["asks"]
        bidList = open_orders["bids"]

        if askList:
            if len(askList) > remain_size:
                for i in range(len(askList) - remain_size):
                    order_id_list += str(askList[i][1]) + ","

        if bidList:
            if len(bidList) > remain_size:
                for i in range(len(bidList) - remain_size):
                    order_id_list += str(bidList[i][1]) + ","

        order_id_list = order_id_list[0:len(order_id_list) - 1]
        if order_id_list:
            print(await self.cancel(order_id_list))

    async def my_depth(self):
        ALL_DEPTH_RESOURCE = "/api/get_user_all_depth"
        params = {
            "api_key": self.__apikey
        }
        params['sign'] = self.__buildMySign(params)
        return await self.__post_http(ALL_DEPTH_RESOURCE, params)

    async def all_depth(self):
        ALL_DEPTH_RESOURCE = "/api/get_all_depth"
        req = {}
        return await self.__get_http(ALL_DEPTH_RESOURCE, req)

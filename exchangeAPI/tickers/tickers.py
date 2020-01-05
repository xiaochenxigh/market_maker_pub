
from ExchangeApi.http_utils import http_request


async def tickers_binance():

    url = 'https://api.binance.com/api/v3/ticker/bookTicker'
    res = await http_request('GET', url)
    t = {}
    for xi in res:
        t[xi['symbol']] = [float(xi['bidPrice']), float(xi['askPrice'])]
    return t



async def tickers_zb():
    url = 'http://api.zb.cn/data/v1/allTicker'
    res = await http_request('GET', url)
    t = {}
    for x in res:
        t[x] = [float(res[x]['buy']), float(res[x]['sell'])]
    return t



async def tickers_huobi():
    url = 'https://api.huobi.pro/market/tickers'
    res = await http_request('GET', url)
    if not res:
        return False
    t = {}
    if 'data' in res:
        if res['data']:
            for x in res['data']:
                if isinstance(x,dict):
                    t[x['symbol']] = [float(x['close']), float(x['close'])]
    return t


async def tickers_sok():
    url = 'https://openapi.sok.top/open/api/get_allticker'
    res = await http_request('GET', url)
    if not res:
        return False
    t = {}
    if isinstance(res, dict):
        if 'data' in res:
            if res['data']:
                if 'ticker' in res['data']:
                    if res['data']['ticker']:
                        for i in res['data']['ticker']:
                            if 'buy' in i and 'sell' in i:
                                t[i['symbol']] = [float(i['buy']), float(i['sell'])]
    return t


async def tickers_excash():
    url = 'https://api_lan.ex.cash/api/get_market'
    res = await http_request('GET',url)
    if not res:
        return False
    t = {}
    if isinstance(res, dict):
        if 'markets' in res:
            if res['markets']:
                for i in res['markets']:
                    t[i['symbol']] = [float(i['last_price']), float(i['last_price'])]
    return t
from exchangeAPI.exchangeapi import create_order, cancel_order, cancel_remain
import random
import asyncio
from databaseAPI.db_config import rds
import logging


def safe_value(dictionary, key, default_value=None):
    if isinstance(dictionary, dict):
        return dictionary[key] if key is not None and (key in dictionary) and dictionary[
            key] is not None else default_value


def sss(start, end, target, decimal):
    t1 = round(target, decimal)
    p10 = 10 ** decimal
    base_gap = 1 / p10
    active_gap = round(end - start - base_gap, decimal)

    if active_gap < 0:
        return False
    if active_gap == 0:
        return start
    if start < t1 < end:
        return t1
    if t1 <= start:
        remain = start - t1
        base_int = int(remain / active_gap)
        base_remain = remain % active_gap
        if base_int % 2 == 0:
            if base_remain == 0:
                return round(start + base_gap, decimal)
            else:
                return round(start + base_remain, decimal)
        else:
            if base_remain == 0:
                return round(end - base_gap, decimal)
            else:
                return round(end - base_remain, decimal)
    if t1 >= end:
        remain = t1 - end
        base_int = int(remain / active_gap)
        base_remain = remain % active_gap
        if base_int % 2 == 0:
            if base_remain == 0:
                return round(end - base_gap, decimal)
            else:
                return round(end - base_remain, decimal)
        else:
            if base_remain == 0:
                return round(start + base_gap, decimal)
            else:
                return round(start + base_remain, decimal)


def ticker_depth(ticker, depth_num, base_diff, every_diff, decimal):
    if not ticker:
        return False

    buy_list = [round(ticker[0] - base_diff - every_diff * i, decimal)
                for i in range(depth_num)]
    sell_list = [round(ticker[1] + base_diff + every_diff * i, decimal)
                 for i in range(depth_num)]

    return {'bids': buy_list, 'asks': sell_list}


async def get_ticker_b(price_reverse, symbol_a, exchange_b, symbol_b, decimal, ratio, base_symbol, base_price,
                       target_price, down_limit, up_limit):
    depth_t = safe_value(await rds.get(exchange_b), symbol_b)
    if not depth_t:
        return False
    if price_reverse == 0:
        return [round(depth_t[0] * ratio, decimal), round(depth_t[1] * ratio, decimal)]
    if price_reverse == 3:
        depth_2 = safe_value(await rds.get(base_symbol.split(',')[0]), base_symbol.split(',')[1])
        return [round(depth_t[0] * depth_2[0] * ratio, decimal), round(depth_t[1] * depth_2[1] * ratio, decimal)]
    if price_reverse == 2:
        base_price_s = float(base_price.split(
            ',')[0]) if ',' in base_price else float(base_price)
        fand_da = float(base_price.split(',')[1]) if ',' in base_price else 1.0
        depth_2 = safe_value(await rds.get(base_symbol.split(',')[0]), base_symbol.split(',')[1])
        p = (1 + (depth_2[0] - base_price_s) /
             base_price_s * fand_da) * target_price
        p = sss(down_limit, up_limit, p, decimal)
        if down_limit <= p <= up_limit:
            return [p, p]


def copy_list(list1, list2, every_diff):
    if not list2:
        logging.error('copy_list()__list2 is None')
        return False
    if not list1:
        logging.error('copy_list()__list1 is None')
        return False

    list_tmp = []
    for p in list2:
        if isinstance(list1[0],list):
            if not [x[0] for x in list1 if abs(float(x[0]) - p) < every_diff]:
                if p > 0.0:
                    list_tmp.append(p)
        if isinstance(list1[0],float):
            if not [x for x in list1 if abs(float(x) - p) < every_diff]:
                if p > 0.0:
                    list_tmp.append(p)
    return list_tmp


def cancel_list(list1, list2, every_diff):
    price_start = list2[0] - every_diff / 2 if list2[0] < list2[-1] else list2[-1] - every_diff
    price_end = list2[-1] + every_diff if list2[0] < list2[-1] else list2[0] + every_diff / 2
    return [x[1] for x in list1 if float(x[0]) < price_start or float(x[0]) > price_end]


def real_ticker(list1, min_size):
    asks = safe_value(list1, 'asks')
    bids = safe_value(list1, 'bids')
    buy1 = sell1 = -1
    if isinstance(asks, list):
        for i in asks:
            if i[1] > min_size:
                sell1 = i[0]
                break
    if isinstance(bids, list):
        for i in bids:
            if i[1] > min_size:
                buy1 = i[0]
                break
    return buy1, sell1


async def farm_min(ccc, user_dict, base_range):
    exchange_a = ccc['exchangeA']
    symbol_a = ccc['symbolA']
    userid_a = ccc['useridA']
    frequent = int(ccc['frequent'])
    api_key = user_dict[userid_a]['api_key']
    secret_key = user_dict[userid_a]['secret_key']
    if ccc['onoff'] != '1':
        await cancel_remain(exchange_a, api_key, secret_key, symbol_a, 0)
        return False

    judge_frequent = random.randint(0, frequent)
    if judge_frequent > 1:
        await cancel_remain(exchange_a, api_key, secret_key, symbol_a, 0)
        return False

    depth_a = await rds.get('DEPTHA_{}_{}'.format(exchange_a, symbol_a))
    buy1, sell1 = real_ticker(depth_a, float(ccc['eat_limit_amount']))

    ticker_b = await get_ticker_b(int(ccc['price_reverse']),
                                  symbol_a,
                                  ccc['exchangeB'],
                                  ccc['symbolB'],
                                  int(ccc['priceDecimal']),
                                  float(ccc['price_ratio']),
                                  ccc['base_symbol'],
                                  ccc['base_price'],
                                  float(ccc['target_price']),
                                  float(ccc['down_limit']),
                                  float(ccc['up_limit']))
    farm_price = sss(buy1, sell1, (ticker_b[0] + ticker_b[1]) / 2, int(ccc['priceDecimal']))
    farm_amount = round(random.uniform(float(ccc['minSize']), float(ccc['minSize']) + (float(ccc['maxSize']) - float(ccc['minSize'])) / 5 * base_range), int(ccc['amountDecimal']))
    if farm_price >= sell1 or farm_price <= buy1:
        await cancel_remain(exchange_a, api_key, secret_key, symbol_a, 0)
        return False

    tasks = []
    if random.randint(0, 1) == 0:
        tasks.append(asyncio.ensure_future(create_order(exchange_a, api_key, secret_key, symbol_a, farm_price, farm_amount, 'buy')))
        tasks.append(asyncio.ensure_future(create_order(exchange_a, api_key, secret_key, symbol_a, farm_price, farm_amount, 'sell')))
    else:
        tasks.append(asyncio.ensure_future(create_order(exchange_a, api_key, secret_key, symbol_a, farm_price, farm_amount, 'sell')))
        tasks.append(asyncio.ensure_future(create_order(exchange_a, api_key, secret_key, symbol_a, farm_price, farm_amount, 'buy')))

    await asyncio.gather(*tasks)

    await asyncio.sleep(3)
    await cancel_remain(exchange_a, api_key, secret_key, symbol_a, 0)


async def copy_min(ccc, user_dict):
    price_decimal = int(ccc['priceDecimal'])
    symbol = ccc['symbol']
    exchange_a = ccc['exchangeA']
    symbol_a = ccc['symbolA']
    userid_a = ccc['useridA']
    exchange_b = ccc['exchangeB']
    userid_b = ccc['useridB']
    symbol_b = ccc['symbolB']
    onoff = ccc['onoff']
    min_size_buy = float(ccc['minSize_buy'])
    max_size_buy = float(ccc['maxSize_buy'])
    min_size_sell = float(ccc['minSize_sell'])
    max_size_sell = float(ccc['maxSize_sell'])
    base_diff = float(ccc['priceWin'])
    every_diff = float(ccc['everyDiff'])
    price_range = float(ccc['priceRand'])
    depth_num = int(ccc['depth'])
    amount_decimal = int(ccc['amountDecimal'])
    ratio = float(ccc['price_ratio'])
    price_strategy = ccc['price_reverse']
    base_symbol = ccc['base_symbol']
    base_price = ccc['base_price']
    target_price = float(ccc['target_price'])
    up_limit = float(ccc['up_limit'])
    down_limit = float(ccc['down_limit'])
    # hedging = ccc['hedging']
    api_key = user_dict[userid_a]["api_key"]
    secret_key = user_dict[userid_a]["secret_key"]

    if onoff != '1':
        logging.error("COPY_MAIN_MIN_ONOFF={}".format(onoff))
        await cancel_remain(exchange_a, api_key, secret_key, symbol_a, 0)
        return False

    ticker_b = await get_ticker_b(price_strategy, symbol_a, exchange_b, symbol_b, price_decimal, ratio, base_symbol,base_price, target_price, down_limit, up_limit)
    depth_b = ticker_depth(ticker_b, depth_num, base_diff,every_diff, price_decimal)
    depth_a = await rds.get("DEPTHA_{}_{}".format(exchange_a, symbol_a))
    depth_m = await rds.get("DEPTHM_{}_{}".format(api_key, symbol_a))
    if not depth_b:
        print(symbol_a, symbol_b, depth_b)
        return False
    ask_list_all = []
    bid_list_all = []
    ask_list_my = []
    bid_list_my = []
    if depth_a:
        ask_list_all = depth_a['asks'] if isinstance(depth_a, dict) else []
        bid_list_all = depth_a['bids'] if isinstance(depth_a, dict) else []
    if depth_m:
        ask_list_my = depth_m['asks'] if isinstance(depth_m, dict) else []
        bid_list_my = depth_m['bids'] if isinstance(depth_m, dict) else []

    buy_list = copy_list(bid_list_all, depth_b['bids'], every_diff)
    if buy_list:
        buy_list = copy_list(bid_list_my, buy_list, every_diff)
    sell_list = copy_list(ask_list_all, depth_b['asks'], every_diff)
    if sell_list:
        sell_list = copy_list(ask_list_my, sell_list, every_diff)
    cancel1 = cancel_list(bid_list_my, depth_b["bids"], every_diff)
    cancel2 = cancel_list(ask_list_my, depth_b["asks"], every_diff)

    tasks = []
    if buy_list:
        for i in buy_list:
            amount = round(random.uniform(min_size_buy, max_size_buy), amount_decimal)
            price = round(random.uniform(i - price_range,i + price_range), price_decimal)
            tasks.append(asyncio.ensure_future(create_order(exchange_a, api_key, secret_key, symbol_a, price, amount, "buy")))
    if sell_list:
        for i in sell_list:
            amount = round(random.uniform(min_size_sell, max_size_sell), amount_decimal)
            price = round(random.uniform(i - price_range,i + price_range), price_decimal)
            tasks.append(asyncio.ensure_future(create_order(exchange_a, api_key, secret_key, symbol_a, price, amount, "sell")))

    if cancel1:
        for i in cancel1:
            tasks.append(asyncio.ensure_future(cancel_order(exchange_a, api_key, secret_key, symbol_a, i)))

    if cancel2:
        for i in cancel2:
            tasks.append(asyncio.ensure_future(cancel_order(exchange_a, api_key, secret_key, symbol_a, i)))
    await asyncio.gather(*tasks)

from exchangeAPI.cc import cc
from exchangeAPI.chainex import chainex
from exchangeAPI.coin100 import coin100
from exchangeAPI.coinbig import coinbig
from exchangeAPI.fubt import fubt
from exchangeAPI.goko import goko
from exchangeAPI.hitbtc import hitbtc
from exchangeAPI.hotcoin import hotcoin
from exchangeAPI.junex import junex
from exchangeAPI.latoken import latoken
from exchangeAPI.lbank import lbank
from exchangeAPI.loex import loex
from exchangeAPI.qbtc import qbtc
from exchangeAPI.sok import sok
from exchangeAPI.wbfex import wbfex
from exchangeAPI.zg import zg
from exchangeAPI.zt import zt
from exchangeAPI.bw import bw
from exchangeAPI.zbg import zbg
from exchangeAPI.jdwex import jdwex
from exchangeAPI.excash import excash
from exchangeAPI.icotau import icotau
from exchangeAPI.fcoin import fcoin
from exchangeAPI.tickers import tickers
import asyncio
from databaseAPI.db_config import rds


async def ticker_b(exchange):
    try:
        res = None
        if exchange == "BINANCE":
            res = tickers.tickers_binance()
        if exchange == 'HUOBIPRO':
            res = tickers.tickers_huobi()
        if exchange == 'ZB':
            res = tickers.tickers_zb()
        if exchange == 'SOK':
            res = tickers.tickers_sok()
        if exchange == 'EXCASH':
            res = tickers.tickers_excash()
        await rds.set('{}'.format(exchange), res, 10)
        return res
    except Exception as e:
        print("ERROR:::tickers----{}_{}".format(exchange, e))


async def depth_a(exchange, symbol, api_key, secret_key):
    try:
        res = None
        if exchange == "EXCASH":
            cli = excash.Excash(api_key, secret_key)
            res = await cli.depth_all(symbol)

        if exchange == 'FCOIN':
            await asyncio.sleep(0.01)
            cli = fcoin.Fcoin(api_key, secret_key)
            res = cli.depth_all(symbol)

        if exchange == "ICOTAU":
            cli = icotau.Icotau(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == "SOK":
            cli = sok.Sok(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == "WBFEX":
            cli = wbfex.Wbfex(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == "HOTCOIN":
            cli = hotcoin.Hotcoin(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == "COIN100":
            cli = coin100.Coin100(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == "COINBIG":
            cli = coinbig.Coinbig(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == "FUBT":
            cli = fubt.FubtApi(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == "GOKO":
            cli = goko.Goko(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == "LBANK":
            cli = lbank.Lbank(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == "LOEX":
            cli = loex.Loex(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == "QBTC":
            cli = qbtc.Qbtc(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == "ZG":
            cli = zg.Zgcom(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == "ZT":
            cli = zt.Zt(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == "CC":
            cli = cc.Cc(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == "LATOKEN":
            cli = latoken.Latoken(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == 'HITBTC':
            cli = hitbtc.Hitbtc(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == "BW":
            cli = bw.Bw(api_key, secret_key)
            res = await cli.depth_all_ws(symbol)
        if exchange == 'JUNEX':
            cli = junex.Junex(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == 'CHAINEX':
            cli = chainex.Chainex(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == 'ZBG':
            cli = zbg.Zbg(api_key, secret_key)
            res = await cli.depth_all(symbol)
        if exchange == 'JDWEX':
            cli = jdwex.Jdwex(api_key, secret_key)
            res = await cli.depth_all(symbol)
        await rds.set('DEPTHA_{}_{}'.format(exchange, symbol), res, 10)
        return res
    except Exception as e:
        print("ERROR:::get_depth_all----{}_{}_{}".format(exchange, symbol, e))


async def depth_m(exchange, symbol, api_key, secret_key):
    try:
        res = None
        if exchange == "EXCASH":
            cli = excash.Excash(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == 'FCOIN':
            cli = fcoin.Fcoin(api_key, secret_key)
            await asyncio.sleep(0.01)
            res = cli.depth_my(symbol)
        if exchange == "SOK":
            cli = sok.Sok(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "ICOTAU":
            cli = icotau.Icotau(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "WBFEX":
            cli = wbfex.Wbfex(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "HOTCOIN":
            cli = hotcoin.Hotcoin(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "BW":
            cli = bw.Bw(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "COIN100":
            cli = coin100.Coin100(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "COINBIG":
            cli = coinbig.Coinbig(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "FUBT":
            cli = fubt.FubtApi(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "GOKO":
            cli = goko.Goko(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "LBANK":
            cli = lbank.Lbank(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "LOEX":
            cli = loex.Loex(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "QBTC":
            cli = qbtc.Qbtc(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "ZG":
            cli = zg.Zgcom(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "ZT":
            cli = zt.Zt(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "CC":
            cli = cc.Cc(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "LATOKEN":
            cli = latoken.Latoken(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == 'HITBTC':
            cli = hitbtc.Hitbtc(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == "BW":
            cli = bw.Bw(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == 'JUNEX':
            cli = junex.Junex(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == 'CHAINEX':
            cli = chainex.Chainex(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == 'ZBG':
            cli = zbg.Zbg(api_key, secret_key)
            res = await cli.depth_my(symbol)
        if exchange == 'JDWEX':
            cli = jdwex.Jdwex(api_key, secret_key)
            res = await cli.depth_my(symbol)
        await rds.set('DEPTHM_{}_{}'.format(api_key, symbol), res, 10)
        return res
    except Exception as e:
        print("ERROR:::get_depth_my----{}_{}_{}".format(exchange, symbol, e))


async def create_order(exchange, api_key, secret_key, symbol, price, amount, side):
    try:
        if exchange == "EXCASH":
            cli = excash.Excash(api_key, secret_key)
            if side == "buy":
                return await cli.create_order(symbol, price, amount, 1)
            if side == "sell":
                return await cli.create_order(symbol, price, amount, 2)
        if exchange == 'FCOIN':
            cli = fcoin.Fcoin(api_key, secret_key)
            if side == 'buy':
                return cli.buy(symbol, price, amount)
            if side == 'sell':
                return cli.sell(symbol, price, amount)
        if exchange == "SOK":
            cli = sok.Sok(api_key, secret_key)
            return await cli.create_order(symbol, price, amount, side)
        if exchange == "ICOTAU":
            cli = icotau.Icotau(api_key, secret_key)
            return await cli.create_order(symbol, price, amount, side)
        if exchange == "CC":
            cli = cc.Cc(api_key, secret_key)
            return await cli.create_order(symbol, price, amount, side)
        if exchange == "WBFEX":
            cli = wbfex.Wbfex(api_key, secret_key)
            return await cli.create_order(symbol, price, amount, side)
        if exchange == "HOTCOIN":
            cli = hotcoin.Hotcoin(api_key, secret_key)
            return await cli.create_order(symbol, price, amount, side)
        if exchange == "COIN100":
            cli = coin100.Coin100(api_key, secret_key)
            return await cli.create_order(symbol, price, amount, side.upper())
        if exchange == "COINBIG":
            cli = coinbig.Coinbig(api_key, secret_key)
            return await cli.create_order(symbol, price, amount, side)
        if exchange == "FUBT":
            cli = fubt.FubtApi(api_key, secret_key)
            return await cli.create_order(symbol, price, amount, side)
        if exchange == "GOKO":
            cli = goko.Goko(api_key, secret_key)
            return await cli.create_order(symbol, price, amount, side)
        if exchange == "LBANK":
            cli = lbank.Lbank(api_key, secret_key)
            return await cli.create_order(symbol, price, amount, side)
        if exchange == "LOEX":
            cli = loex.Loex(api_key, secret_key)
            return await cli.create_order(symbol, price, amount, side)
        if exchange == "QBTC":
            cli = qbtc.Qbtc(api_key, secret_key)
            if side == "buy":
                return await cli.create_order(symbol, price, amount, 1)
            if side == "sell":
                return await cli.create_order(symbol, price, amount, 2)
        if exchange == "ZG":
            cli = zg.Zgcom(api_key, secret_key)
            if side == "buy":
                return await cli.create_order(symbol, price, amount, 2)
            if side == "sell":
                return await cli.create_order(symbol, price, amount, 1)
        if exchange == "ZT":
            cli = zt.Zt(api_key, secret_key)
            if side == "buy":
                return await cli.create_order(symbol, price, amount, 2)
            if side == "sell":
                return await cli.create_order(symbol, price, amount, 1)
            if side == "buy":
                return await cli.create_order(symbol, price, amount, 1)
            if side == "sell":
                return await cli.create_order(symbol, price, amount, 2)
        if exchange == "LATOKEN":
            cli = latoken.Latoken(api_key, secret_key)
            return await cli.create_order(symbol, price, amount, side)
        if exchange == 'HITBTC':
            cli = hitbtc.Hitbtc(api_key, secret_key)
            return await cli.create_order(symbol, price, amount, side)
        if exchange == "BW":
            cli = bw.Bw(api_key, secret_key)
            if side == "buy":
                return await cli.create_order(symbol, price, amount, 1)
            if side == "sell":
                return await cli.create_order(symbol, price, amount, 0)
        if exchange == 'JUNEX':
            cli = junex.Junex(api_key, secret_key)
            if side == 'buy':
                side = 0
            if side == 'sell':
                side = 1
            return await cli.create_order(symbol, price, amount, side)
        if exchange == 'CHAINEX':
            if side == 'buy':
                side = 1
            if side == 'sell':
                side = 2
            cli = chainex.Chainex(api_key, secret_key)
            return await cli.create_order(symbol, price, amount, side)
        if exchange == 'ZBG':
            cli = zbg.Zbg(api_key, secret_key)
            if side == 'buy':
                side = 1
            if side == 'sell':
                side = 0
            return await cli.create_order(symbol, price, amount, side)
        if exchange == 'JDWEX':
            cli = jdwex.Jdwex(api_key, secret_key)
            if side == 'buy':
                side = 0
            if side == 'sell':
                side = 1
            return await cli.create_order(symbol, price, amount, side)
    except Exception as e:
        print(
            "ERROR:::create_order----{}_{}_{}_{}_{}_{}_{}_{}".format(exchange, api_key, secret_key, symbol, price,
                                                                     amount,
                                                                     side, e))


async def cancel_order(exchange, api_key, secret_key, symbol, order_id, side=None):
    try:
        if exchange == "EXCASH":
            cli = excash.Excash(api_key, secret_key)
            return await cli.cancel(order_id)
        if exchange == 'FCOIN':
            cli = fcoin.Fcoin(api_key, secret_key)
            await asyncio.sleep(0.01)
            return cli.cancel_order(order_id)
        if exchange == "SOK":
            cli = sok.Sok(api_key, secret_key)
            return await cli.cancel_order(symbol, order_id)
        if exchange == "ICOTAU":
            cli = icotau.Icotau(api_key, secret_key)
            return await cli.cancel_order(symbol, order_id)
        if exchange == "CC":
            cli = cc.Cc(api_key, secret_key)
            return await cli.cancel_order(symbol, order_id)
        if exchange == "WBFEX":
            cli = wbfex.Wbfex(api_key, secret_key)
            return await cli.cancel_order(symbol, order_id)
        if exchange == "HOTCOIN":
            cli = hotcoin.Hotcoin(api_key, secret_key)
            return await cli.cancel_order(order_id)
        if exchange == "COIN100":
            cli = coin100.Coin100(api_key, secret_key)
            return await cli.cancel_order(symbol, order_id)
        if exchange == "COINBIG":
            cli = coinbig.Coinbig(api_key, secret_key)
            return await cli.cancel_order(order_id)
        if exchange == "FUBT":
            cli = fubt.FubtApi(api_key, secret_key)
            return await cli.cancel_order(order_id)
        if exchange == "GOKO":
            cli = goko.Goko(api_key, secret_key)
            return await cli.cancel_order(symbol, order_id)
        if exchange == "LBANK":
            cli = lbank.Lbank(api_key, secret_key)
            return await cli.cancel_order(symbol, order_id)
        if exchange == "LOEX":
            cli = loex.Loex(api_key, secret_key)
            return await cli.cancel_order(symbol, order_id)
        if exchange == "QBTC":
            cli = qbtc.Qbtc(api_key, secret_key)
            return await cli.cancel_order(order_id)
        if exchange == "ZG":
            cli = zg.Zgcom(api_key, secret_key)
            return await cli.cancel_order(symbol, order_id)
        if exchange == "ZT":
            cli = zt.Zt(api_key, secret_key)
            return await cli.cancel_order(symbol, order_id)
        if exchange == "LATOKEN":
            cli = latoken.Latoken(api_key, secret_key)
            return await cli.cancel_order(order_id)
        if exchange == 'HITBTC':
            cli = hitbtc.Hitbtc(api_key, secret_key)
            return await cli.cancel_order(order_id)
        if exchange == "BW":
            cli = bw.Bw(api_key, secret_key)
            return await cli.cancel_order(symbol, order_id)
        if exchange == 'JUNEX':
            cli = junex.Junex(api_key, secret_key)
            if side == 'buy':
                return await cli.cancel_order(symbol, order_id, 0)
            if side == 'sell':
                return await cli.cancel_order(symbol, order_id, 1)
        if exchange == 'CHAINEX':
            cli = chainex.Chainex(api_key, secret_key)
            return await cli.cancel_order(order_id)
        if exchange == 'ZBG':
            cli = zbg.Zbg(api_key, secret_key)
            return cli.cancel_order(symbol, order_id)
        if exchange == 'JDWEX':
            cli = jdwex.Jdwex(api_key, secret_key)
            return await cli.cancel_order(order_id)
    except Exception as e:
        print("ERROR:::create_order----{}_{}_{}_{}_{}_{}".format(exchange, api_key, secret_key, symbol, order_id, e))


async def balances(exchange, api_key, secret_key):
    try:
        if exchange == "EXCASH":
            cli = excash.Excash(api_key, secret_key)
            return await cli.balance()
        if exchange == 'FCOIN':
            cli = fcoin.Fcoin(api_key, secret_key)
            await asyncio.sleep(0.01)
            return cli.get_balance()
        if exchange == "SOK":
            cli = sok.Sok(api_key, secret_key)
            return await cli.balances()
        if exchange == "ICOTAU":
            cli = icotau.Icotau(api_key, secret_key)
            return await cli.balances()
        if exchange == "CC":
            cli = cc.Cc(api_key, secret_key)
            return await cli.balances()
        if exchange == "WBFEX":
            cli = wbfex.Wbfex(api_key, secret_key)
            return await cli.balances()
        if exchange == "HOTCOIN":
            cli = hotcoin.Hotcoin(api_key, secret_key)
            return await cli.balances()
        if exchange == "COIN100":
            cli = coin100.Coin100(api_key, secret_key)
            return await cli.balances()
        if exchange == "COINBIG":
            cli = coinbig.Coinbig(api_key, secret_key)
            return await cli.balances()
        if exchange == "FUBT":
            cli = fubt.FubtApi(api_key, secret_key)
            return await cli.balances()
        if exchange == "GOKO":
            cli = goko.Goko(api_key, secret_key)
            return await cli.balances()
        if exchange == "LBANK":
            cli = lbank.Lbank(api_key, secret_key)
            return await cli.balances()
        if exchange == "LOEX":
            cli = loex.Loex(api_key, secret_key)
            return await cli.balances()
        if exchange == "QBTC":
            cli = qbtc.Qbtc(api_key, secret_key)
            return await cli.balances()
        if exchange == "ZG":
            cli = zg.Zgcom(api_key, secret_key)
            return await cli.balances()
        if exchange == "ZT":
            cli = zt.Zt(api_key, secret_key)
            return await cli.balances()
        if exchange == "LATOKEN":
            cli = latoken.Latoken(api_key, secret_key)
            return await cli.balances()
        if exchange == 'HITBTC':
            cli = hitbtc.Hitbtc(api_key, secret_key)
            return await cli.balances()
        if exchange == "BW":
            cli = bw.Bw(api_key, secret_key)
            return await cli.balances()
        if exchange == 'JUNEX':
            cli = junex.Junex(api_key, secret_key)
            return await cli.balances()
        if exchange == 'CHAINEX':
            cli = chainex.Chainex(api_key, secret_key)
            return await cli.balances()
        if exchange == 'ZBG':
            cli = zbg.Zbg(api_key, secret_key)
            return await cli.balances()
        if exchange == 'JDWEX':
            cli = jdwex.Jdwex(api_key, secret_key)
            return await cli.balances()
    except Exception as e:
        print("ERROR:::balances----{}_{}_{}_{}".format(exchange, api_key, secret_key, e))


async def cancel_remain(exchange, api_key, secret_key, symbol, remain_size=0):
    try:
        if exchange == "EXCASH":
            cli = excash.Excash(api_key, secret_key)
            return await cli.cancel_remain(symbol, remain_size)
        if exchange == 'FCOIN':
            cli = fcoin.Fcoin(api_key, secret_key)
            await asyncio.sleep(0.01)
            data = cli.depth_my(symbol)
            if not data:
                return False
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        cli.cancel_order(data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        cli.cancel_order(data["asks"][i][1])

        if exchange == "SOK":
            cli = sok.Sok(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(symbol, data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(symbol, data["asks"][i][1])

        if exchange == "ICOTAU":
            cli = icotau.Icotau(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(symbol, data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(symbol, data["asks"][i][1])

        if exchange == "CC":
            cli = cc.Cc(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(symbol, data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(symbol, data["asks"][i][1])
        if exchange == "WBFEX":
            cli = wbfex.Wbfex(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(symbol, data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(symbol, data["asks"][i][1])

        if exchange == "HOTCOIN":
            cli = hotcoin.Hotcoin(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(data["asks"][i][1])
        if exchange == "COIN100":
            cli = coin100.Coin100(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(symbol, data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(symbol, data["asks"][i][1])
        if exchange == "COINBIG":
            cli = coinbig.Coinbig(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(data["asks"][i][1])
        if exchange == "FUBT":
            cli = fubt.FubtApi(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(data["asks"][i][1])
        if exchange == "GOKO":
            cli = goko.Goko(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(symbol, data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(symbol, data["asks"][i][1])
        if exchange == "LBANK":
            cli = lbank.Lbank(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(symbol, data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(symbol, data["asks"][i][1])
        if exchange == "LOEX":
            cli = loex.Loex(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(symbol, data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(symbol, data["asks"][i][1])
        if exchange == "QBTC":
            cli = qbtc.Qbtc(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(data["asks"][i][1])
        if exchange == "ZG":
            cli = zg.Zgcom(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(symbol, data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(symbol, data["asks"][i][1])
        if exchange == "ZT":
            cli = zt.Zt(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(symbol, data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(symbol, data["asks"][i][1])
        if exchange == "LATOKEN":
            cli = latoken.Latoken(api_key, secret_key)
            data = await cli.depth_my(symbol)

            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(data["asks"][i][1])
        if exchange == 'HITBTC':
            cli = hitbtc.Hitbtc(api_key, secret_key)
            data = await cli.depth_my(symbol)

            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(data["asks"][i][1])
        if exchange == "BW":
            cli = bw.Bw(api_key, secret_key)
            data = await cli.depth_my(symbol)

            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(symbol, data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(symbol, data["asks"][i][1])

        if exchange == "JUNEX":
            cli = junex.Junex(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if not data:
                return False
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(symbol, data["bids"][i][1], 0)
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(symbol, data["asks"][i][1], 1)

        if exchange == 'CHAINEX':
            cli = chainex.Chainex(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(data["asks"][i][1])

        if exchange == 'ZBG':
            cli = zbg.Zbg(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(symbol, data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(symbol, data["asks"][i][1])

        if exchange == 'JDWEX':
            cli = jdwex.Jdwex(api_key, secret_key)
            data = await cli.depth_my(symbol)
            if data["bids"]:
                for i in range(len(data["bids"])):
                    if i < len(data["bids"]) - remain_size:
                        await cli.cancel_order(data["bids"][i][1])
            if data["asks"]:
                for i in range(len(data["asks"])):
                    if i < len(data["asks"]) - remain_size:
                        await cli.cancel_order(data["asks"][i][1])
    except Exception as e:
        print("ERROR:::create_order----{}_{}_{}_{}_{}_{}".format(exchange, api_key, secret_key, symbol, remain_size, e))

from exchangeAPI.exchangeapi import depth_a, depth_m, balances, ticker_b
from databaseAPI.db_config import rds, msql
import asyncio
from threading import Thread


async def ticker_tasks():
    while True:
        tasks = [
            ticker_b("BINANCE"),
            ticker_b('HUOBIPRO'),
            ticker_b('ZB'),
            ticker_b('EXCASH')
        ]
        await asyncio.gather(*tasks)
        await asyncio.sleep(3)


async def depth_all_tasks():
    while True:
        depth_list = await rds.get('OPENORDERLIST')
        if not depth_list:
            return False

        tasks = []
        for i in depth_list:
            tasks.append(asyncio.ensure_future(depth_a(i['exchange'], i['symbolA'], i['api_key'], i['secret_key'])))
        await asyncio.gather(*tasks)
        await asyncio.sleep(3)


async def depth_my_tasks():
    while True:
        depth_list = await rds.get('OPENORDERLIST')
        if not depth_list:
            return False

        tasks = []
        for i in depth_list:
            tasks.append(asyncio.ensure_future(depth_a(i['exchange'], i['symbolA'], i['api_key'], i['secret_key'])))
        await asyncio.gather(*tasks)
        await asyncio.sleep(3)


async def balances_tasks():
    while True:
        bal_list = await rds.get('BALANCELIST')
        if not bal_list:
            return False

        tasks = []
        for i in range(len(bal_list)):
            tasks.append(
                asyncio.ensure_future(
                    balances(bal_list[i]['exchange'], bal_list[i]['api_key'], bal_list[i]['secret_key'])))
        data = await asyncio.gather(*tasks)
        bal = {}
        for x in range(len(bal_list)):
            bal[bal_list[x]['user_id']] = data[x]
        await rds.set('balances', bal, 1000)
        await asyncio.sleep(100)


async def get_setting():
    while True:
        if not await rds.get('COPYLIST'):
            await rds.set('COPYLIST', await msql.fetch_all("select * from copyconfig"), 20)
        if not await rds.get('OPENORDERLIST'):
            await rds.set('OPENORDERLIST', await msql.fetch_all(
                "select b.exchange,a.useridA,b.api_key,b.secret_key,b.user_id,b.user_name,a.symbolA from copyconfig a left join user b on a.useridA = b.user_id"),
                          20)
        if not await rds.get('FARMLIST'):
            await rds.set('FARMLIST', await msql.fetch_all("select * from farmconfig"), 20)
        if not await rds.get('BALANCELIST'):
            await rds.set('BALANCELIST', await msql.fetch_all("select exchange,user_id,api_key,secret_key from user"),
                          20)
        if not await rds.get('USERLIST'):
            user_dict = await msql.fetch_all("select * from farmconfig")
            temp = {}
            for i in user_dict:
                temp[i['user_id']] = i
            await rds.set('USERLIST', temp, 20)
        await asyncio.sleep(3)


def start_loop(loop):
    asyncio.set_event_loop(loop=loop)
    loop.run_forever()


def main():
    new_loop = asyncio.new_event_loop()
    t = Thread(target=start_loop, args=(new_loop,))
    t.start()

    asyncio.run_coroutine_threadsafe(ticker_tasks(), new_loop)
    asyncio.run_coroutine_threadsafe(balances_tasks(), new_loop)
    asyncio.run_coroutine_threadsafe(get_setting(), new_loop)


if __name__ == '__main__':
    main()
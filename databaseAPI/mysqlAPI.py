import asyncio
import aiomysql


class Mysql:
    def __init__(self, **config):
        self.__config = config
        self.__pool = None

    async def _create_pool(self):
        if not self.__pool:
            self.__pool = await aiomysql.create_pool(10, 50, host=self.__config['host'],
                                                     port=self.__config['port'],
                                                     user=self.__config['user'],
                                                     password=self.__config['password'],
                                                     db=self.__config['db'],
                                                     cursorclass=aiomysql.DictCursor,
                                                     loop=asyncio.get_event_loop())

    async def fetch_one(self, sql, params=None):
        await self._create_pool()
        async with self.__pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, params)
                result = await cur.fetchone()
                await conn.commit()
                await conn.close()
                return result

    async def fetch_all(self, sql, params=None):
        await self._create_pool()
        async with self.__pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, params)
                result = await cur.fetchall()
                await conn.commit()
                await conn.close()
                return result

    async def execute(self, sql, params=None):
        await self._create_pool()
        async with self.__pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    result = await cur.execute(sql, params)
                except Exception as e:
                    await conn.rollback()
                    raise Exception(
                        'error__Mysql__excute()___sql={}__error={}'.format(sql, repr(e)))
                finally:
                    await conn.commit()
                    await conn.close()
                    return result

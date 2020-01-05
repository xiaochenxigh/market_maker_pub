import asyncio
import aioredis
import json


class Redis:
    def __init__(self, **config):
        self.__config = config
        self.__pool = None

    async def _create_pool(self):
        if not self.__pool:
            self.__pool = await aioredis.create_redis_pool((self.__config['host'], self.__config['port']),
                                                           db=self.__config['db'], minsize=5, maxsize=30,
                                                           loop=asyncio.get_event_loop())

    async def get(self,key):
        await self._create_pool()
        data = await self.__pool.get(key)
        if not data:
            return None
        return json.loads(data)

    async def set(self,key,value,ex_time=None):
        await self._create_pool()
        await self.__pool.set(key,json.dumps(value))
        if ex_time:
            await self.__pool.expire(key,ex_time)
import os
import json
import asyncio
import discord
import aiohttp
from time import time as Time
from discord.ext import commands
from const import TOKEN, PREFIX, IF_BOT
from random_headers import random_headers

class Bot:
    def __init__(self, *, prefix, token, if_bot):
        self.if_bot    = if_bot
        self.token     = token
        self.loop      = asyncio.get_event_loop()
        self.cookies   = aiohttp.DummyCookieJar()
        self.connector = aiohttp.TCPConnector()
        self.session   = aiohttp.ClientSession(loop       = self.loop,
                                               connector  = self.connector,
                                               cookie_jar = self.cookies)

        self.core      = commands.Bot(command_prefix        = prefix,
                                      fetch_offline_members = True,
                                      loop                  = self.loop,
                                      connector             = self.connector)

    def cmd(self, **kwargs):
        def wrapper(func):
            @self.core.command(name = func.__name__, **kwargs)
            async def inner_wrapper(ctx, *args):
                start = Time()

                await func(ctx, *args)

                print(f'COMMAND "{func.__name__}": {round(Time() - start, 2)}\n\t{args}')

            return inner_wrapper
        return wrapper

    def run(self):
        try:
            self.loop.run_until_complete(self.core.start(os.environ[self.token], bot = self.if_bot))
        except KeyboardInterrupt:
            print('\n')
        except Exception as err:
            from time import asctime
            with open('err.log', '+a') as f:
                f.write(f'ERROR: {err}\nDATE: {asctime()}\n\n{json.dumps(dict(os.environ), indent = 2)}\n\n')
        finally:
            self.loop.run_until_complete(self.core.logout())
            self.loop.run_until_complete(self.session.close())
            self.loop.run_until_complete(self.connector.close())
            self.loop.close()

    async def get(self, url: str) -> aiohttp.ClientResponse:
        return await self.session.get(url, headers = random_headers())

    async def get_page(self, url: str) -> str:
        page = await self.get(url)
        return await page.text()

    async def get_all(self, urls: list) -> list:
        return await asyncio.gather(*[self.get(u) for u in urls])

    async def get_all_pages(self, urls: list) -> list:
        resps = await self.get_all(urls)
        return await asyncio.gather(*[r.text() for r in resps])

# initializing the bot

bot = Bot(prefix = PREFIX,
          token  = TOKEN,
          if_bot = IF_BOT)

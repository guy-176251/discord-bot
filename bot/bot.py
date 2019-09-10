import os
import json
import asyncio
import discord
import aiohttp
from time import time as Time
from discord.ext import commands

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
            with open('err.log', '+a') as f:
                f.write(f'ERROR: {err}\n\n{json.dumps(dict(os.environ), indent = 2)}\n')
        finally:
            self.loop.run_until_complete(self.core.logout())
            self.loop.run_until_complete(self.session.close())
            self.loop.run_until_complete(self.connector.close())
            self.loop.close()

    async def get(self, url: str) -> aiohttp.ClientResponse:
        return await self.session.get(url, headers = random_headers())

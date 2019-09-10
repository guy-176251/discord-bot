import discord
import asyncio
from .bot import Bot
from const import TOKEN, PREFIX, IF_BOT
from discord.ext.commands import Context
from overwatch import the_facts, the_stats
from .scorekeeper import scorekeeper, embed_maker, WIN, LOSE

# initializing the bot

bot = Bot(prefix = PREFIX,
          token  = TOKEN,
          if_bot = IF_BOT)

@bot.core.event
async def on_ready():
    print('we in boi')

@bot.cmd(aliases = ['s'])
async def stats(ctx: Context, *args):
    async with ctx.typing():
        if len(args) == 0:
            pass

        if args[0] == 'all':
            btag   = args[1]
            per_10 = True
        else:
            btag   = args[0]
            per_10 = False

        resp = await bot.get(f'https://playoverwatch.com/en-us/career/pc/{btag.replace("#", "-")}')
        page = await resp.text()

        await ctx.send(embed = the_stats(btag, page, per_10))

@bot.cmd(aliases = ['f'])
async def facts(ctx: Context, *args):
    async with ctx.typing():
        resp = await bot.get(f'https://overwatch.gamepedia.com/{args[0]}')

        if resp.status == 404:
            await ctx.send(
                embed=discord.Embed(
                    title='Not Found',
                    description=(f'`{args[0]}` was not found. Check for typos, '
                                 'the hero name is not case sensitive.')
                )
            )
        elif resp.status == 200:
            page   = await resp.text()
            embeds = the_facts(args[0], page)

            for e in embeds:
                try:
                    await ctx.send(embed=e)
                except Exception as err:
                    print(f'facts error: {err}\n\n{e}')

@bot.cmd(aliases = ['sc'])
async def score(ctx: Context, *args):

    if 'help' in args:
        await ctx.send(embed=discord.Embed(
            title = '__Usage__',
            description = (f'`{bot.core.command_prefix}score (user mention) ("win" or "lose")` to update the score\n'
                           f'`{bot.core.command_prefix}score` to get your record without updating\n'
                           f'`{bot.core.command_prefix}score (user mention) clear` to clear the record with that user'
        )))
        return

    win_words  = ('win', 'won')
    lose_words = ('lose', 'loss')

    if args and ctx.message.mentions:
        if any(kw in args for kw in win_words + lose_words):
            if any(kw in args for kw in win_words):
                mode = True
            else:
                mode = False

            scorekeeper.score(ctx.author.id, ctx.message.mentions.pop().id, mode)

        elif 'clear' in args:
            scorekeeper.clear(ctx.author.id, ctx.message.mentions.pop().id)

    embeds = embed_maker(ctx)

    if not embeds:
        await ctx.send(embed = discord.Embed(
            title = f'__Record for {ctx.message.author.nick or ctx.message.author.name}__',
            description = 'No record for user.'
        ))
        return

    for em in embeds:
        await ctx.send(embed=em)
        await asyncio.sleep(0.5)

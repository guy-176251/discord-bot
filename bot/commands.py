import random
import discord
import asyncio
from .bot import bot
from discord.ext import commands
from discord.ext.commands import Context
from overwatch import the_facts, the_stats
from textmod import font_df, font_fk, font_ss
from .scorekeeper import scorekeeper, embed_maker, WIN, LOSE

@bot.core.event
async def on_ready():
    print('we in boi')

@bot.cmd(aliases=['ss'])
async def superscript(ctx, *args):
    words = ctx.message.content.lower()[len(ctx.invoked_with) + 1:]
    await ctx.send(''.join((font_ss.get(c, c) for c in words)))

@bot.cmd(aliases = ['s'])
async def stats(ctx: Context, *args):
    async with ctx.typing():
        urls = [f'https://playoverwatch.com/en-us/career/pc/{btag.replace("#","-")}'
                for btag in list(set(args))[:12]]

        pages = []

        pages.extend(await bot.get_all_pages(urls[:6]))
        pages.extend(await bot.get_all_pages(urls[6:]))

        embeds = [the_stats(page) for page in pages]

        for em in sorted(embeds, key = lambda e: len(e.fields), reverse=False):
            await ctx.send(embed = em)
            await asyncio.sleep(0.5)

@bot.cmd(aliases=['df'])
async def deepfry(ctx, *args):
    words = ctx.message.content.upper()[len(ctx.invoked_with) + 1:]
    await ctx.send(''.join(((random.choice(font_df[c]) if c in font_df else c) for c in words)))

def fuckifier(word):
    result = ''
    for c in word:
        temp = []
        for n in range(random.randint(1, 4)):
            thing = random.choice(font_fk)
            if thing not in temp:
                temp.append(thing)

        result += ''.join(temp)
        result += c

    return result

@bot.cmd(aliases=['fk'])
async def fucked(ctx, *args):
    await ctx.send(' '.join((fuckifier(a) for a in args)))

@bot.cmd(aliases = ['os'])
async def old_stats(ctx: Context, *args):
    async with ctx.typing():
        page = await bot.get_page(f'https://playoverwatch.com/en-us/career/pc/{args[0].replace("#", "-")}')
        await ctx.send(embed = the_stats(args[0], page))

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
            search_term = '' if len(args) < 2 else args[1].lower()
            embeds = the_facts(page, search_term)

            if not embeds:
                await ctx.send(embed=discord.Embed(title = args[0].title(),
                                                   description = f'No results found for search term `{search_term}`.'))
                return

            for e in embeds:
                try:
                    await ctx.send(embed=e)
                except Exception as err:
                    print(f'facts error: {err}\n\n{e}')

        else:
            await ctx.send(embed = discord.Embed(title = 'Network Issues',
                                                 description = 'Wait a few minutes and try again.'))

@bot.cmd(aliases = ['sc'])
async def score(ctx: Context, *args):

    if 'help' in args:
        await ctx.send(embed=discord.Embed(
            title = '__Usage__',
            description = (
                f'`{bot.core.command_prefix}score (user mention) ("win" or "lose")` to update the score\n'
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

is_me = lambda ctx: ctx.message.author.id == 510834536993783818

@bot.cmd(aliases = ['ev'])
@commands.check(is_me)
async def evaluate(ctx: Context, *args):
    cmd = ctx.message.content.replace(f'{bot.core.command_prefix}{ctx.invoked_with} ', '')
    print('  Evaluating "{cmd}"...')
    try:
        result = eval(cmd)
    except Exception as err:
        await ctx.send(f'`Error with "{cmd}": "{err}"`')
        return
    else:
        await ctx.send(f'`{result}`')

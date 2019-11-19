import json
import discord
from typing import Tuple
from bs4.element import Tag
from itertools import islice
from time import time as Time
from bs4 import BeautifulSoup as Soup, SoupStrainer as Filter

if __name__ == '__main__':
    from roles import all_heroes
    from graphs import graph, stats_tables
else:
    from .roles import all_heroes
    from .graphs import graph, stats_tables

bar_name  = Filter('div', attrs = {'class': 'ProgressBar-title'})
bar_stats = Filter('div', attrs = {'class': 'ProgressBar-description'})

def embed_desc_and_img(btag: str, soup: Tag, career: Tag) -> Tuple[str, str]:
    '''
    Returns the embed description and rank image url, both as str.
    '''
    rank         = soup.find('div', attrs = {'class': 'competitive-rank'})
    games_played = int(career.find("tr", attrs = {"data-stat-id": "0x0860000000000385"}).contents[1].text)
    games_won    = int(career.find('tr', attrs = {'data-stat-id': '0x08600000000003F5'}).contents[1].text)
    time_pld     = career.find('tr', attrs = {'data-stat-id': '0x0860000000000026'}).contents[1].text
    playow       = f'https://playoverwatch.com/en-us/career/pc/{btag.replace("#", "-")}'
    overbuff     = f'https://www.overbuff.com/players/pc/{btag.replace("#", "-")}?mode=competitive'

    try:
        sr = f'{rank.div.text} SR'
        img = rank.img['src']
    except:
        sr = '__Unranked__'
        img = ''

    return ((f'[PlayOverwatch]({playow}) | [Overbuff]({overbuff})\n\n'
             f'**{sr}**\n\n'
             f'{games_played} competitive games played '
             f'({round(games_won/games_played * 100, 2)}% won) over {time_pld}'),
            img)

def all_graphs(career: Tag) -> Tuple[str, str, dict]:

    '''
    gets timed played for all heroes
    '''

    top_5 = dict(islice(
        ((hero.find(bar_name).text, {
            'time':    hero.find(bar_stats).text,
            'percent': float(hero['data-overwatch-progress-percent']),
            'id':      hero.img['src'].split('/')[-1].split('.')[0]})
        for hero in career.find('div', attrs = {'data-category-id': '0x0860000000000021'}).children
    ), 5))

    all_heroes = {
        hero.find(bar_name).text: {'time': float(hero['data-overwatch-progress-percent'])}
        for hero in career.find('div', attrs = {'data-category-id': '0x0860000000000021'}).children
    }

    '''
    gets win percentages for all heroes
    '''
    for hero in career.find('div', attrs = {'data-category-id': '0x08600000000003D1'}).children:

        name = hero.find(bar_name).text
        win  = hero.find(bar_stats).text

        if name in top_5:
            top_5[name]['win'] = win

        all_heroes[name]['win'] = (int(win.replace('%', '')) / 100) * all_heroes[name]['time']

    '''
    converts individual hero stats into role stats
    '''

    _all_classes = {}
    for hero in all_heroes:

        role = all_heroes[hero]

        _all_classes.setdefault(role, {'time': 0, 'win': 0})

        for n in ('time', 'win'):
            _all_classes[role][n] += all_heroes[hero][n]

    '''
    converts decimal values to percentages
    '''

    time_list  = lambda: (_all_classes[role]['time'] for role in _all_classes)
    total_time = sum(time_list())
    max_time   = max(time_list())
    time_pld   = clock_to_mins(career.find('tr', attrs = {'data-stat-id': '0x0860000000000026'}).contents[1].text)

    all_classes = {
        role: {
            'time'    : mins_to_clock(_all_classes[role]['time'] / total_time * time_pld),
            'percent' : _all_classes[role]['time'] / max_time,
            'win'     : str(int(_all_classes[role]['win'] / _all_classes[role]['time'] * 100)) + '%'
        }
        for role in _all_classes
    }

    return graph(top_5), graph(all_classes), {hero: top_5[hero]['id'] for hero in top_5}

def clock_to_mins(str_time: str) -> float:
    times = str_time.split(':')[::-1]
    total = int(times[0]) / 60

    try:
        total += int(times[1])
    except:
        return total

    try:
        total += int(times[2]) * 60
    except:
        return total

    return total

def mins_to_clock(total: float) -> str:
    if total >= 60:
        return f'{int(total / 60):0>2}:{int(total % 60):0>2}:{int((total - int(total)) * 60):0>2}'
    else:
        return f'{int(total):0>2}:{int((total - int(total)) * 60):0>2}'

def stats_per_10_mins(career: Tag, ID: str) -> dict:
    all_stats  = {}
    stats_10   = {}
    per_10     = ' - Avg per 10 Min'
    stats_soup = career.find('div', attrs = {'data-category-id': ID})

    for table in stats_soup.children:
        for tr in table.tbody.children:
            stat = tr.contents[0].text.replace(' Done', '').strip()
            info = tr.contents[1].text

            for word in ('Blow', 'Kill'):
                if word in stat and f'{word}s' not in stat:
                    stat = stat.replace(word, f'{word}s').strip()

            all_stats[stat] = info

            if per_10 in stat or ('Accuracy' in stat and 'Best' not in stat):
                stats_10[stat.replace(per_10, '').strip()] = None

            if stat == 'Time Played':
                total_time = clock_to_mins(info) / 10

    for stat in stats_10:
        if '%' in all_stats[stat]:
            stats_10[stat] = all_stats[stat]
        elif ':' in all_stats[stat]:
            stats_10[stat] = mins_to_clock(clock_to_mins(all_stats[stat]) / total_time)
        else:
            stats_10[stat] = round(float(all_stats[stat]) / total_time, 2)

    return stats_10

def stats_scraper(btag: str, page: bytes, per_10: bool = False) -> Tuple[str, str, str, str, list]:
    '''return tuple(embed_description : str,
                    rank_url          : str,
                    top_5_graph       : str,
                    all_classes_graph : str,
                    top_5_stats       : list)'''

    start      = Time()
    soup_start = Time()

    soup = Soup(page, 'lxml')

    soup_finish = round(Time() - soup_start, 2)

    if soup.h1.text == 'Profile Not Found':
        return 'not found'

    if soup.p.text == 'Private Profile':
        return 'private'

    career = soup.find('div', attrs = {'id': 'competitive', 'data-js': 'career-category'})

    top_5, all_classes, top_5_IDs = all_graphs(career)

    embed_desc, rank_url = embed_desc_and_img(btag, soup, career)

    if per_10:
        per_10 = stats_tables({hero: stats_per_10_mins(career, top_5_IDs[hero])
                               for hero in top_5_IDs})

    print(f'time: {round(Time() - start, 2)}\nsoup time: {soup_finish}')

    return (embed_desc,
            rank_url,
            top_5,
            all_classes,
            per_10)

def embed_maker(btag: str, stats: tuple) -> discord.Embed:
    blank = ' 󠀀󠀀'

    embed_desc, rank_url, top_5, all_classes, per_10 = stats

    embed = discord.Embed(description = embed_desc)
    embed.set_author(name = btag, icon_url = rank_url)

    embed.add_field(name = f'{blank}\n__Top 5 Most Played__\n{blank}',
                    value = f'```ml\n{top_5}```', inline=False)

    embed.add_field(name = f'{blank}\n__All Roles__\n{blank}',
                    value = f'```ml\n{all_classes}```', inline=False)

    if per_10:

        for ind, h in enumerate(per_10):
            if ind == 0:
                name = f'{blank}\n__Stats Per 10 Mins__\n{blank}'
            else:
                name = blank

            embed.add_field(name=name, value=f'```ml\n{h}```')

    return embed

def the_stats(btag: str, page: bytes, per_10: bool = False) -> discord.Embed:
    stats = stats_scraper(btag, page, per_10)

    caveats = {
        'private': 'Your account is set to private, so the bot cannot get information about your account.',
        'not found': 'Either there is a typo in your account name, or the bot is being rate limited by Blizzard servers.'
    }

    if stats in caveats:
        desc = (
            f'{caveats[stats]}'
            '\n\nYou can click on the link below to your account to verify yourself.\n\n'
            f'[PlayOverwatch](https://playoverwatch.com/en-us/career/pc/{btag.replace("#", "-")})')
        return discord.Embed(title = btag, description = desc)

    return embed_maker(btag, stats)

if __name__ == '__main__':
    import requests
    import argparse
    from os import environ
    from discord import Webhook, RequestsWebhookAdapter

    btag = 'Leon#14910'

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--btag', help = 'Specify a Battle.net Tag')

    args = parser.parse_args()
    if args.btag:
        btag = args.btag

    url  = f'https://playoverwatch.com/en-us/career/pc/{btag.replace("#", "-")}'

    webhook = Webhook.from_url(environ['WEBHOOK_URL'], adapter = RequestsWebhookAdapter())
    webhook.send(embed = the_stats(btag, requests.get(url).content, True))

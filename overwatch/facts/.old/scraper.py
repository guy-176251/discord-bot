#import json
import discord
from typing import List
from bs4 import BeautifulSoup as Soup

if __name__ == '__main__':
    from utils import *
else:
    from .utils import *

def facts_scraper(page: bytes) -> list:
    '''Returns a list of lists, each holding keyword arguments for discord.Embed().add_field()'''
    soup  = Soup(page, 'lxml', parse_only = PAGE_BODY)

    abilities = (
        (f'{elem.span.text} - {elem.p.text}',
         abl_key[ len( elem.find(INFOBOXTABLE).contents ) > 1 ](elem))

        for elem in soup.contents[-1].find_all(ABL_DETAILS))

    return [
        [{'inline': False, 'name': f'{blank}\n__{name}__', 'value': f'{blank}\n{abl}'}]
        if type(abl) == str else
        [{'inline': False, 'name': f'{blank}\n__{name}__', 'value': blank}] + field(abl)

        for name, abl in abilities
    ]

def embed_maker(hero: str, facts: list) -> List[discord.Embed]:
    '''Returns a list of discord Embed objects'''
    embeds = [discord.Embed(title = hero.title())]

    for abl in facts:

        if len(embeds[-1].fields) + len(abl) > 25:
            embeds.append(discord.Embed(title = f'{hero.title()} Cont.'))

        for f in abl:
            embeds[-1].add_field(**f)

    return embeds

def the_facts(hero: str, page: bytes) -> List[discord.Embed]:
    return embed_maker(hero, facts_scraper(page))

if __name__ == '__main__':
    import requests
    import argparse
    from os import environ
    from discord import Webhook, RequestsWebhookAdapter

    hero = 'reinhardt'

    parser = argparse.ArgumentParser()
    parser.add_argument('--hero', help = 'Specify a hero to search.')

    args = parser.parse_args()
    if args.hero:
        hero = args.hero

    facts = the_facts(hero, requests.get(f'https://overwatch.gamepedia.com/{hero}').content)

    webhook = Webhook.from_url(environ['WEBHOOK_URL'], adapter = RequestsWebhookAdapter())
    webhook.send(embeds=facts)

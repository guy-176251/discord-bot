import discord
from bs4.element import Tag
from bs4 import BeautifulSoup as Soup, SoupStrainer as Filter

if __name__ == '__main__':
    from classes import hero_classes
    from graphs import graph, stats_tables
    from utils import *
else:
    from .classes import hero_classes
    from .graphs import graph, stats_tables
    from .utils import *

def scraper(page: bytes) -> dict:
    soup = Soup(page, 'lxml', parse_only = SITE)
    comp = soup.find(COMP)

    all_roles = {
        get_role_name(role) : {
            'rank': {
                'sr': int(role.text.strip()),
                'image': role.find(RANK_IMG)['src']
            },
            'heroes': {}
        }
        for role in soup.find(RANK)
    }

    for role in hero_classes.roles:
        all_roles.setdefault(role, {'rank': {'sr':'__Unranked__','image':''}, 'heroes':{}})

    # wins are first in order to calculate win percentage and get time played in one loop
    for hero in comp.find(WIN):

        name = hero.find(NAME).text
        role = hero_classes[name]

        all_roles[role]['heroes'][name] = {'win': hero.find(DESC).text}

    for hero in comp.find(TIME):

        name = hero.find(NAME).text
        role = hero_classes[name]

        percent = float(hero['data-overwatch-progress-percent'])
        win = int(all_roles[role]['heroes'][name]['win'].replace('%','')) / 100

        all_roles[role]['heroes'][name].update({'time': hero.find(DESC).text,
                                                'percent_total': percent,
                                                'percent_win': percent * win})

    return all_roles

if __name__ == '__main__':
    import pprint
    import requests
    import argparse
    from os import environ
    from discord import Webhook, RequestsWebhookAdapter
    from random_headers import get

    btag = 'CupNoodle-11826'

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--btag', help = 'Specify a Battle.net Tag')

    args = parser.parse_args()
    if args.btag:
        btag = args.btag

    url  = f'https://playoverwatch.com/en-us/career/pc/{btag.replace("#", "-")}'

    #webhook = Webhook.from_url(environ['WEBHOOK_URL'], adapter = RequestsWebhookAdapter())
    #webhook.send(embed = the_stats(btag, requests.get(url).content, True))

    pprint.pprint(scraper(get(url)), indent = 2)

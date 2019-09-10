import json
import discord
from typing import List
from bs4.element import Tag
from time import time as Time
from bs4 import BeautifulSoup as Soup, SoupStrainer as Filter

__blank = ' 󠀀󠀀'

# details
# abl.find('div', attrs = {'class': 'mw-collapsible-content'}).ul.contents

def facts_scraper(hero: str, page: bytes) -> dict:
    soup  = Soup(page, 'lxml', parse_only = Filter('div', attrs = {'class': 'mw-parser-output'}))

    abilities = (
        (f'{elem.span.text} - {elem.p.text}',
         (subelem for subelem
          in elem.find('table', attrs = {'class':'infoboxtable'}).contents[1].contents
          if type(subelem) == Tag))

        for elem in soup.contents[-1].find_all('div', attrs={'class':'ability_details'})
        if len(elem.find('table', attrs = {'class':'infoboxtable'}).contents) > 1)

    facts = []

    for name, abl in abilities:

        temp = [{'inline': False, 'name': f'{__blank}\n__{abl}__', 'value': __blank}]

        for fact in abl:

            temp = {'inline': True, 'name': fact.contents[0].text}

            if '<br' in str(fact.contents[2]):
                temp['value'] = '\n'.join(str(thing).strip()
                                          for thing in fact.contents[2]
                                          if type(thing) != Tag and str(thing).strip() != '')

            else:
                temp['value'] = fact.contents[2].text

            facts.append(temp)

    # print(json.dumps(facts, indent = 2))
    return facts

def embed_maker(hero: str, facts: dict) -> List[discord.Embed]:
    embeds = [discord.Embed(title = hero.title())]

    for abl in facts:

        if len(embeds[-1].fields) + len(facts[abl]) + 1 > 25:
            embeds.append(discord.Embed(title = f'{hero.title()} Cont.'))

        embeds[-1].add_field(name = f'{__blank}\n__{abl}__', value = __blank, inline=False)
        for f in facts[abl]:
            embeds[-1].add_field(name = f, value = '\n'.join(facts[abl][f]), inline = True)

        #temp = {'type': 'rich', 'title': hero.title()}

    return embeds

def the_facts(hero: str, page: bytes) -> List[discord.Embed]:
    return embed_maker(hero, facts_scraper(hero, page))

if __name__ == '__main__':
    import requests
    from os import environ
    from discord import Webhook, RequestsWebhookAdapter

    hero = 'ana'
    url  = f'https://overwatch.gamepedia.com/{hero}'

    facts = the_facts(hero, requests.get(url).content)

    webhook = Webhook.from_url(environ['WEBHOOK_URL'], adapter = RequestsWebhookAdapter())
    webhook.send(embeds=facts)

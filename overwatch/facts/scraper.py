import discord
from lxml import html

def find(elem, css):
    return elem.cssselect(css)[0] if elem.cssselect(css) else None

def scraper(doc: html.HtmlElement, search_term: str) -> tuple:
    '''(Hero Name, Dictionary)'''
    return find(doc, 'h1').text, {
        f'{find(abl, "span.mw-headline").text} - {find(abl, "p").text}':

            [tuple('\n'.join(l.strip() for l in td.text_content().split('\n'))
                   for td in tr.cssselect('td'))
             for tr in find(abl, 'table.infoboxtable')[0]]

        for abl in doc.cssselect('div.mw-parser-output')[-1].cssselect('div.ability_details')
        if any(search_term in s for s in [find(abl, 'span.mw-headline').text.lower(),
                                          find(abl, 'p').text.lower()])
    }

def discord_embed(page: str, search_term: str) -> list:
    '''[List of Discord Embeds]'''
    name, facts = scraper(html.fromstring(page.replace('<br />', '\n')), search_term)
    embeds = [discord.Embed(title = name)]
    blank = '󠀀'

    for abl in facts:

        if len(embeds[-1].fields) + len(facts[abl]) > 25:
            embeds.append(discord.Embed(title = f'{name} Cont.'))

        embeds[-1].add_field(name=f'{blank}\n__{abl}__', value=blank, inline=False)

        for n, v in facts[abl]:
            embeds[-1].add_field(name=n, value=v)

    if len(embeds) == 1 and len(embeds[0].fields) == 0:
        return []

    return embeds

def the_facts(page: str, search_term: str) -> list:
    return discord_embed(page, search_term)

if __name__ == '__main__':
    import os
    from pprint import pprint
    from discord import Webhook, RequestsWebhookAdapter

    with open('html/orisa.html', 'r') as IN:
        page = IN.read().replace('<br />', '\n')

    with open('html/facts.txt', 'w') as OUT:
        pprint(scraper(html.fromstring(page)), OUT)

    webhook = Webhook.from_url(os.environ['TEST_WEBHOOK'], adapter = RequestsWebhookAdapter())
    webhook.send(embeds = discord_embed(page))

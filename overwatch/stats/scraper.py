import discord
from lxml import html
from urllib.parse import unquote

try:
    from .utils import *
    from .roles import all_heroes
except:
    from utils import *
    from roles import all_heroes

def scraper(page: str) -> dict:
    doc  = html.fromstring(page)

    url = find(doc, 'link[rel=canonical]').get('href')
    btag = unquote(url.split('/')[-1]).replace('-','#')

    if 'profile not found' in find(doc, 'h1').text.lower():
        return {'found': False, 'btag': btag}

    profile_pic = find(doc, 'img.player-portrait').get('src')

    if 'private profile' in find(doc, 'p.masthead-permission-level-text').text.lower():
        return {
            'found' : True,
            'image' : profile_pic,
            'btag'  : btag
        }

    comp = find(doc, '#competitive')

    if not comp:
        return {
            'found' : True,
            'public': True,
            'btag'  : btag,
            'image' : profile_pic
        }

    roles = {role: {'sr':'Unranked','image':'','heroes':{}} for role in all_heroes.roles}

    rank = find(doc, '.competitive-rank')

    if rank:
        roles.update({role_name(r): {'sr'    : int(find(r, 'div.competitive-rank-level').text),
                                     'image' : find(r, '.competitive-rank-tier-icon').get('src'),
                                     'heroes': {}}

                      for r in rank})

    comp_stats = zip(*[sorted(find(comp, css), key = lambda elem: find(elem, bar_name).text)
                       for css in (
                           '[data-category-id="0x08600000000003D1"]', # winpercent
                           '[data-category-id="0x0860000000000021"]', # timeplayed
                       )])

    heroes = {find(wp, bar_name).text: {'time'        : find(tp, bar_value).text,
                                        'win'         : f"{find(wp, bar_value).text.strip('%')}%",
                                        'time percent': float(tp.get('data-overwatch-progress-percent')),
                                        'win percent' : int(find(wp, bar_value).text.replace('%','')) / 100}

              for wp, tp in comp_stats}

    for h in heroes:
        roles[all_heroes[h]]['heroes'][h] = heroes[h]

    empty_roles = [r for r in roles if not roles[r]['heroes']]

    for r in empty_roles:
        roles.pop(r)

    for r in roles:
        heroes = roles[r]['heroes']

        total_percent = sum(heroes[h]['time percent'] for h in heroes)
        total_time    = sum(str_to_sec(heroes[h]['time']) for h in heroes)
        win_percent   = sum(heroes[h]['time percent'] * heroes[h]['win percent'] for h in heroes)

        try:
            win_rate = win_percent / total_percent
        except ZeroDivisionError:
            win_rate = 0

        roles[r].update({
            'time'        : sec_to_str(total_time),
            'win'         : f'{int(round(win_rate * 100, 0))}%',
            'time percent': total_percent,
            'win percent' : win_rate
        })

    if any(type(roles[r]['sr']) == int for r in roles):
        ranked_roles = [r for r in roles if type(roles[r]['sr']) == int]
        highest_role = sorted(ranked_roles, key = lambda r: roles[r]['sr'])[-1]
    else:
        highest_role = None

    games_played = int(find(comp, '[data-stat-id="0x0860000000000385"]')[1].text)
    games_won = find(comp, '[data-stat-id="0x08600000000003F5"]')

    return {
        'found'       : True,
        'public'      : True,
        'comp'        : True,
        'old'         : (True if games_played >= len(roles) * 5
                              and all(roles[r]['sr'] == 'Unranked' for r in roles)
                              else False),
        'btag'        : btag,
        'games played': games_played,
        'games won'   : int(games_won[1].text) if games_won else 0,
        'time'        : find(comp, '[data-stat-id="0x0860000000000026"]')[1].text,
        'roles'       : roles,
        'highest'     : roles[highest_role]['image'] if highest_role else '',
        'image'       : profile_pic
    }

def graph(stats: dict) -> str:
    '''
    time percent
    win percent
    time
    win
    '''
    sorted_stats = sorted(stats.keys(),
                          key = lambda cat: stats[cat]['time percent'],
                          reverse = True)[:5]

    bar_len   = 16
    name_len  = max(len(cat) for cat in sorted_stats)
    time_len  = max(len(f"{stats[cat]['time']}") for cat in sorted_stats)
    win_len   = max(len(stats[cat]['win']) for cat in sorted_stats)
    max_time  = max(stats[cat]['time percent'] for cat in sorted_stats)
    cols      = (name_len, bar_len, time_len, win_len)

    def bar(cat):
        bar_num  = int(cat['time percent'] * bar_len / max_time)
        lose_num = int(bar_num * (1 - cat['win percent']))
        return   (f'{"".join(win for _ in range(bar_num - lose_num))}'
                  f'{"".join(lose for _ in range(lose_num))}')

    return '\n'.join((
        box_edges(U, cols),
        '\n'.join(edge_v.join((f'{edge_v}{cat: <{name_len}}',
                               f'{bar(stats[cat]): <{bar_len}}',
                               f'{stats[cat]["time"]: >{time_len}}',
                               f'{stats[cat]["win"]: >{win_len}}{edge_v}'))
                  for cat in sorted_stats),
        box_edges(D, cols)
    ))

def discord_stats(page_or_stats) -> discord.Embed:
    try:    page_or_stats['found']
    except: stats = scraper(page_or_stats)
    else:   stats = page_or_stats

    embed = discord.Embed()
    embed.set_author(name     = stats['btag'],
                     icon_url = stats.get('highest', ''),
                     url      = f'https://playoverwatch.com/en-us/career/pc/{stats["btag"].replace("#","-")}')

    if not stats['found']:
        embed.description = 'Profile not found. Check for typos and try again.'
        return embed

    embed.set_image(url = stats['image'])

    if not stats.get('public', False):
        embed.description = f'{blank}\nThis profile is currently private and cannot be seen.'
        return embed

    if not stats.get('comp', False):
        embed.description = f'{blank}\nThis profile is public but has no competitive info.'
        return embed

    embed.description = (f'{blank}\n{stats["games played"]} competitive game(s) played '
                         f'({round(stats["games won"] / stats["games played"] * 100, 2)}% won) '
                         f'over {stats["time"]}\n{blank}')

    if stats['old']:
        embed.description += f'\n**This competitive info is from a previous season.**\n{blank}'

    sorted_roles = sorted(stats['roles'].keys(),
                          key = lambda r: stats['roles'][r]['time percent'],
                          reverse = True)

    SRs = '\n'.join(f'{r + ":": <8} {stats["roles"][r]["sr"]}' for r in sorted_roles)

    embed.add_field(name = '__All Roles__',
                    value = f'```ml\n{SRs if not stats["old"] else ""}\n{graph(stats["roles"])}```\n{blank}')

    for role in sorted_roles:
        embed.add_field(name = f'__{role}__',
                        inline = False,
                        value = '\n'.join([
                            #f"**SR**: {stats['roles'][role]['sr']}",
                            #f"**Time Played**: {stats['roles'][role]['time']}",
                            #f"**Win Rate**: {stats['roles'][role]['win']}",
                            f"```ml",
                            f"{graph(stats['roles'][role]['heroes'])}```",
                            f"{blank}"
                        ]))

    return embed

# **{stats['roles'][role]['sr']}{' SR' if type(stats['roles'][role]['sr']) == int else ''}**

def the_stats(page: str) -> discord.Embed:
    return discord_stats(page)

if __name__ == '__main__':
    import os
    from pprint import pprint
    from testing.random_headers import get
    from discord import Webhook, RequestsWebhookAdapter

    btag = 'LZR#119553'

    webhook = Webhook.from_url(os.environ['TEST_WEBHOOK'], adapter = RequestsWebhookAdapter())

    page = get(f'https://playoverwatch.com/en-us/career/pc/{btag.replace("#","-")}').content

    stats = scraper(page)

    with open('test/results.txt', 'w') as f:
        pprint(stats, f, indent=2)

    webhook.send(embed = discord_stats(stats))

import os
from discord import Webhook, RequestsWebhookAdapter

#██████▁▁▁▁▁▁
#⣿⣿⣿⣿⣿⣿⣦⣀⣀⣀⣀⣀⣀
#⣿⣿⣿⣿⣿⣿⣇⣀⣀⣀⣀⣀⣀
#⬤⬤⬤⬤⬤⬤◐○○○○○○
#■■■■■■◧□□□□□□
#■■■■■■▨□□□□□□
#■■■■■■▥□□□□□□
#██████░░░░░░
#██████░░░░░░
#⬛⬛⬛⬛⬛⬛⬜⬜⬜⬜
#▰▰▰▰▰▰▱▱▱▱▱▱
#◼◼◼◼◼◼▭▭▭▭▭▭
#▮▮▮▮▮▮▯▯▯▯▯▯
#⬤⬤⬤⬤⬤⬤◯◯◯◯◯◯
#⚫⚫⚫⚫⚫⚫⚪⚪⚪⚪⚪⚪

fonts = [
    '█',
    '▉',
    '▊',
    '▋',
    '▌',
    '▍',
    '▎',
    '▏',
]

full = set([
    '█',
    '⣿',
    '█',
    '⣿',
    '⬤',
    '■',
    '■',
    '■',
    '█',
    '█',
    '▰',
    '◼',
    '▮',
    '⬤',
])

empty = set([
    '▁',
    '⣀',
    '⣀',
    '○',
    '□',
    '□',
    '□',
    '░',
    '░',
    '▱',
    '▭',
    '▉',
    '▊',
    '▋',
    '▌',
    '▍',
    '▎',
    '▏',
    '▯',
    '◯',
])

bars = [
    '██████▁▁▁▁▁▁',
    '⣿⣿⣿⣿⣿⣿⣀⣀⣀⣀⣀⣀',
    '⣿⣿⣿⣿⣿⣿⣀⣀⣀⣀⣀⣀',
    '⬤⬤⬤⬤⬤⬤○○○○○○',
    '■■■■■■□□□□□□',
    '■■■■■■□□□□□□',
    '■■■■■■□□□□□□',
    '██████░░░░░░',
    '██████░░░░░░',
    '⬛⬛⬛⬛⬛⬛⬜⬜⬜⬜',
    '▰▰▰▰▰▰▱▱▱▱▱▱',
    '◼◼◼◼◼◼▭▭▭▭▭▭',
    '▮▮▮▮▮▮▯▯▯▯▯▯',
    '⬤⬤⬤⬤⬤⬤◯◯◯◯◯◯',
    '⚫⚫⚫⚫⚫⚫⚪⚪⚪⚪⚪⚪',
]

strs = ['']
chars = set()

def bar_maker(f, e):
    n = 10
    #bars = '\n'.join(''.join(f for _ in range(i)) + ''.join(e for _ in range(n-i)) for i in range(n))

    bars = '\n'.join(f'{"".join(e for _ in range(i)) + "".join(f for _ in range(i)): <13}|' for i in range(5))

    if len(strs[-1]) + len(bars) > 1993:
        strs.append('')

    strs[-1] += f'\n{bars}'

#for f in full:
#    for e in empty:
#        bar_maker(f, e)

for b in bars:
    try:
        f, e = set(b)
    except:
        continue
    else:
        if e not in chars and f not in chars:
            bar_maker(f, e)
            chars.add(f)
            chars.add(e)

webhook = Webhook.from_url(os.environ['WEBHOOK_URL'], adapter = RequestsWebhookAdapter())
for s in strs: webhook.send(f'```{s}```')

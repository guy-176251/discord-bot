btag       = 'a.button.m-white-outline.m-sm.is-active'
name       = '[class$=title]'
value      = '[class$=description]'
percent    = 'data-overwatch-progress-percent'
image      = '.competitive-rank-tier-icon'
role_sr    = 'div.competitive-rank-level'
winpercent = '[data-category-id="0x08600000000003D1"]'
timeplayed = '[data-category-id="0x0860000000000021"]'
gameswon   = '[data-category-id="0x0860000000000039"]'
profile    = 'p.masthead-permission-level-text'

u = 'u'
d = 'd'
l = 'l'
r = 'r'
m = 'm'

corner_lu = '┏'
corner_ru = '┓'
corner_ld = '┗'
corner_rd = '┛'

joint_l = '┣'
joint_r = '┫'
joint_u = '┳'
joint_d = '┻'
joint_m = '╋'

edge_h = '━'
edge_v = '┃'

#lose = '░'
#win  = '█'

lose = '▌'
win  = '█'

#lose = '|'
#win  = '█'

blank = '󠀀'

corner = { u: { l: corner_lu,
                r: corner_ru },
           d: { l: corner_ld,
                r: corner_rd } }

joint = { l: joint_l,
          r: joint_r,
          u: joint_u,
          d: joint_d,
          m: joint_m }

def edge(num):
    return ''.join(edge_h for _ in range(num))

def box_u_d(up_down, cols):
    return ''.join((corner[up_down][l],
                    joint[up_down].join(edge(n) for n in cols),
                    corner[up_down][r]))

def find(elem, css):
    return elem.cssselect(css)[0] if elem.cssselect(css) else None

def role_name(elem):
    return (find(elem, '[data-ow-tooltip=data-ow-tooltip]')
           .get('data-ow-tooltip-text')
           .replace(' Skill Rating',''))

def str_to_sec(string):
    return sum(int(n) * 60**i for i, n in enumerate(string.split(':')[::-1]))

def sec_to_str(num, ind = 0):
    if ind == 2 or num < 60:
        return f'{num}'
    else:
        return f'{sec_to_str(int(num/60), ind + 1):>02}:{int(round(num % 60, 0)):>02}'

def vim_grid(heroes):
    with open('hero_stats.txt','w') as f:
        f.write(
            'Hero|Time|Win Percent|Games Won|Time Percent\n'
            + '\n'.join(f'{h}|' + '|'.join(str(heroes[h][a]) for a in heroes[h]) for h in heroes)
        )

bar_name  = '[class$=title]'
bar_value = '[class$=description]'

U = 'U'
D = 'D'
L = 'L'
R = 'R'
M = 'M'

edge_h = lambda num: ''.join('━' for _ in range(num))
edge_v = '┃'
lose   = '▌'
win    = '█'
blank  = '󠀀'

corner = { U: { L: '┏',
                R: '┓' },
           D: { L: '┗',
                R: '┛' } }

joint = { L: '┣',
          R: '┫',
          U: '┳',
          D: '┻',
          M: '╋' }

def box_edges(up_or_down, cols):
    return ''.join((corner[up_or_down][L],
                     joint[up_or_down].join(edge_h(n) for n in cols),
                    corner[up_or_down][R]))

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

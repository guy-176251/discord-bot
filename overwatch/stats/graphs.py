from typing import Tuple

bar_full  = '█'
bar_empty = '░'

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
_n     = '\n'

max_bar_len = 12

def stats_tables(hero_info: dict) -> Tuple[str]:
    stats = []
    for hero in hero_info:
        info      = hero_info[hero]
        name_len  = max(len(stat) for stat in info)
        value_len = max(len(str(info[stat])) for stat in info)

        if len(hero) > name_len + value_len + 1:
            name_len = len(hero) - 1 - value_len

        stats.append(
            f'{corner_lu}{border(edge_h, name_len)}{edge_h}{border(edge_h, value_len)}{corner_ru}\n'
            f'{edge_v}{hero: <{name_len + value_len + 1}}{edge_v}\n'
            f'{joint_l}{border(edge_h, name_len)}{joint_u}{border(edge_h, value_len)}{joint_r}\n'
            f'{_n.join(f"{edge_v}{stat.title(): >{name_len}}{edge_v}{info[stat]: <{value_len}}{edge_v}" for stat in info)}'
            f'\n{corner_ld}{border(edge_h, name_len)}{joint_d}{border(edge_h, value_len)}{corner_rd}'
        )


    return tuple(stats)

def graph(info_dict: dict) -> str:
    box = ''

    name_len = max(len(n) for n in info_dict)
    time_len = max(len(info_dict[n]['time']) for n in info_dict)
    win_len  = max(len(f'{info_dict[n]["win"]} WR') for n in info_dict)

    box = [(
        f'{corner_lu}'
        f'{joint_u.join(border(edge_h, thing) for thing in (name_len, max_bar_len, time_len, win_len))}'
        f'{corner_ru}'
    )]

    last = tuple(info_dict.keys())[-1]
    for name in info_dict:
        info    = info_dict[name]
        bar     = int(max_bar_len * info['percent'])
        bar_win = int(int(info['win'].replace('%', '')) * bar / 100)

        if name == last:
            cap_l = corner_ld
            cap_r = corner_rd
            mid   = joint_d
        else:
            cap_l = joint_l
            cap_r = joint_r
            mid   = joint_m

        box.append((
            # name
            f'{edge_v}{name: >{name_len}}'

            # bar
            f'{edge_v}{border(bar_full, bar_win) + border(bar_empty, bar - bar_win): <{max_bar_len}}'

            # time and win percent
            f'{edge_v}{info["time"]: >{time_len}}{edge_v}{info["win"] + " WR": >{win_len}}{edge_v}'

            # bottom border
            f'\n{cap_l}{border(edge_h, name_len)}{mid}{border(edge_h, max_bar_len)}{mid}{border(edge_h, time_len)}{mid}{border(edge_h, win_len)}{cap_r}'
        ))

    return '\n'.join(box)

def border(character: str, length: int) -> str:
    return ''.join(character for _ in range(length))

from bs4 import SoupStrainer as Filter

SITE = Filter('section', attrs = {'id': 'site'})
RANK = Filter('div', attrs = {'class': 'competitive-rank'})
ROLE = Filter('div', attrs = {'data-ow-tooltip': 'data-ow-tooltip'})
TIME = Filter('div', attrs = {'data-category-id':'0x0860000000000021'})
WIN  = Filter('div', attrs = {'data-category-id':'0x08600000000003D1'})
COMP = Filter('div', attrs = {'id':'competitive'})
NAME = Filter('div', attrs = {'class':'ProgressBar-title'})
DESC = Filter('div', attrs = {'class':'ProgressBar-description'})

get_role_name = lambda role: role.find(ROLE)['data-ow-tooltip-text'].replace(' Skill Rating', '').strip()

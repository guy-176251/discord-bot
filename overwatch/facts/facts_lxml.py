from lxml import html
from pprint import pprint

def find(elem, css):
    try:
        return elem.cssselect(css)[0]
    except Exception as err:
        print(err)
        return None

def scraper(doc):
    return {
        f'{find(abl, "span").text} - {find(abl, "p").text}':
            [ tuple('\n'.join(l.strip() for l in td.text_content().split('\n'))
                    for td in tr.cssselect('td'))

              for tr in find(abl, 'table.infoboxtable')[0] ]

        for abl in doc.cssselect('div.ability_details')
    }

def the_facts(hero: str, page: bytes) -> list:
    scraper(page.replace(b'<br />', b'\n'))

if __name__ == '__main__':
    with open('doomfist.html', 'r') as f:
        doc = find(html.fromstring(f.read().replace('<br />', '\n')), 'div.mw-parser-output')

    with open('facts.txt', 'w') as f:
        pprint(scraper(doc), f)

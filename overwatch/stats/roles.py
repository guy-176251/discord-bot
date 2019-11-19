from lxml import html
from pprint import pprint

from random_headers import get

class AllHeroes:
    # {hero_name: class}

    def __init__(self):
        self.__load_classes()

    def __getitem__(self, hero: str) -> str:
        if hero not in self.__classes:
            self.__load_classes()

        return self.__classes[hero]

    def __load_classes(self) -> None:
        doc = html.fromstring(get('https://playoverwatch.com/en-us/heroes'))

        self.__classes = {
            h.text_content(): h.get('data-groups').strip('"[]"').title()
            for h in doc.cssselect('#heroes-selector-container')[0]}

        self.roles = set(self.__classes.values())

        print(f'\nAll Roles: {", ".join(self.roles)}\n')

all_heroes = AllHeroes()

import json
import requests
from bs4.element import Tag
from bs4 import BeautifulSoup as Soup, SoupStrainer as Filter

from random_headers import random_headers

class HeroClasses:
    # {hero_name: class}

    def __init__(self):
        self.__load_classes()

    def __getitem__(self, hero: str) -> str:
        if hero not in self.__classes:
            self.__load_classes()

        return self.__classes[hero]

    def __class(self, hero: Tag) -> str:
        return hero.use.attrs['xlink:href'].split('#')[1].capitalize()

    def __name(self, hero: Tag) -> str:
        return hero.find('span', attrs = {'class': 'portrait-title'}).text

    def __load_classes(self) -> None:
        heroes = Soup(

            requests.get('https://playoverwatch.com/en-us/heroes', headers = random_headers()).content,
            'lxml',
            parse_only = Filter('div', attrs = {'id': 'heroes-selector-container'})

        ).contents[1].children

        self.__classes = {
            self.__name(h): self.__class(h)
            for h in heroes
        }

hero_classes = HeroClasses()

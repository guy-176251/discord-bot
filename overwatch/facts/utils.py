from bs4.element import Tag
from bs4 import SoupStrainer as Filter

blank = ' 󠀀󠀀'
abl_key   = {
    True: lambda elem: (subelem for subelem
                        in elem.find('table', attrs = {'class':'infoboxtable'}).contents[1].contents
                        if type(subelem) == Tag),

    False: lambda elem: '\n'.join(subelem.text
                                  for subelem in elem.ul.contents
                                  if type(subelem) == Tag)
}

def value(fact):
    if '<br' in str(fact):
        return ''.join(str(elem).strip() if type(elem) != Tag
                       else '\n' if elem.text == ''
                       else ' ' + elem.text

                       for elem in fact
                       if str(elem).strip() != '')

    else:
        return fact.text

def field(abl):
    return [ {'inline': True,
              'name': fact.contents[0].text,
              'value': value(fact.contents[2])}

             for fact in abl ]

PAGE_BODY = Filter('div', attrs = {'class': 'mw-parser-output'})
INFOBOXTABLE = Filter('table', attrs = {'class':'infoboxtable'})
ABL_DETAILS = Filter('div', attrs={'class':'ability_details'})

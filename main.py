#!/usr/bin/python3
from bs4 import BeautifulSoup
import urllib.request
import re
import json

# ---formal stuff---
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent}
base_url = 'https://bulbapedia.bulbagarden.net/wiki/{}_(Pok%C3%A9mon)'
name = (re.sub('[\s]', '_', input('Nome Pokemon: ').title()))
url = base_url.format(name)
request = urllib.request.Request(url, None, headers)
response = urllib.request.urlopen(request)
data = response.read()
soup = BeautifulSoup(data, 'html.parser')
# ---formal stuff---

# STATS
ref1 = soup.find('span', {'id': 'Base_stats'})
zone1 = ref1.findAllNext('span', {'class': 'mw-headline'})
ref2 = soup.find('span', {'class': 'mw-headline', 'id': 'Pok.C3.A9athlon_stats'})
if not ref2:
    ref2 = soup.find('span', {'class': 'mw-headline', 'id': 'Type_effectiveness'})
zone2 = ref2.findAllPrevious('span', {'class': 'mw-headline'})
forms = [elem for elem in zone1 if elem in zone2]
stats = ['HP', 'Atk', 'Def', 'SpA', 'SpD', 'Spe', 'Total']
if not forms:
    forms = ['Base stats']
values = soup.find_all('div', {'style': 'float:right'})
index = 0
for form in forms:
    try:
        print('\n' + form.text)
    except AttributeError:
        print('\n' + form)
    for stat in stats:
        print(stat + ': ' + values[index].text)
        index += 1
print('')

# ABILITIES
parents_list = soup.find_all('td', {'class': 'roundy'})
for parent in parents_list:
    if 'Ability' in parent.a.attrs.values():
        par = parent
        break
abilities_list = par.find_all('td')
index = 1
for ability in abilities_list:
    if 'display: none' not in ability.attrs.values():
        for i in ability.find_all('a'):
            ab = i.span.text
            if ability.small is None:
                form = 'Ability ' + str(index)
                index += 1
            else:
                form = ability.small.text
            print(form + ': ' + ab)

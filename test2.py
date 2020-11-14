import json
import requests
from bs4 import BeautifulSoup

#url = 'https://sportsbook.draftkings.com/leagues/football/3?category=game-lines&subcategory=game'
#html = BeautifulSoup(requests.get(url).content, 'html.parser')
#
#data = json.loads(html.select('body script')[0].contents[0].split('window.__INITIAL_STATE__ = ')[1].split(';\n')[0])
#
#print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))

url = 'https://sportsbook.draftkings.com/api/odds/v1/leagues/3/offers/gamelines.json'
data = json.loads(requests.get(url).content)

odds = {}
for event in data['events']:
    odds[event['name']] = {}
    for offer in event['offers']:
        if offer['label'] == "Point Spread" and 'main' in offer:
            odds[event['name']]['spread'] = {}
            for i in [0, 1]:
                odds[event['name']]['spread'][offer['outcomes'][i]['label'].split(' ', 1)[1]] = offer['outcomes'][i]['line']
        elif offer['label'] == "Moneyline":
            odds[event['name']]['moneyline'] = {}
            for i in [0, 1]:
                odds[event['name']]['moneyline'][offer['outcomes'][i]['label'].split(' ', 1)[1]] = {'american': offer['outcomes'][i]['oddsAmerican'], 'decimal': offer['outcomes'][i]['oddsDecimal'], 'fractional': offer['outcomes'][i]['oddsFractional']}


print(odds)

import json
import requests

url = 'https://sportsbook.draftkings.com/api/odds/v1/leagues/3/offers/gamelines.json'
data = json.loads(requests.get(url).content)

_odds_by_game = {}
for event in data['events']:
    _odds_by_game[event['name']] = {}
    for offer in event['offers']:
        if offer['label'] == "Point Spread" and 'main' in offer:
            _odds_by_game[event['name']]['spread'] = {}
            for i in [0, 1]:
                _odds_by_game[event['name']]['spread'][offer['outcomes'][i]['label'].split(' ', 1)[1]] = offer['outcomes'][i]['line']
        elif offer['label'] == "Moneyline":
            _odds_by_game[event['name']]['moneyline'] = {}
            for i in [0, 1]:
                _odds_by_game[event['name']]['moneyline'][offer['outcomes'][i]['label'].split(' ', 1)[1]] = {'american': offer['outcomes'][i]['oddsAmerican'], 'decimal': offer['outcomes'][i]['oddsDecimal'], 'fractional': offer['outcomes'][i]['oddsFractional']}

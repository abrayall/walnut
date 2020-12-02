import nfl
import predictions

import pandas

def seeding(conference):
    seeds = []
    standings = pandas.read_html('http://www.playoffstatus.com/nfl/' + conference + 'standings.html')[0]
    for i in range(0, 7):
        seeds.append(nfl.getTeam(standings.iloc[i, 0]))

    return seeds

def game(home, away):
    return nfl.Game('2020', '17', 'December 10', '1:00pm', 'Sat', home, away)

def wildcard_games(seeds):
    return [game(seeds[1], seeds[6]), game(seeds[2], seeds[5]), game(seeds[3], seeds[4])]

def divisional_games(seeds, winners):
    winners = sort(seeds, winners)
    return [
        game(seeds[0], winners[-1]),
        game(winners[0], winners[-2])
    ]

def conference_game(seeds, winners):
    winners = sort(seeds, winners)
    return game(winners[0], winners[1])

def sort(seeds, winners):
    winners.sort(key=lambda team: seeds.index(team))
    return winners

def predict(conference):
    data = {}
    seeds = seeding(conference)
    data['seeds'] = seeds

    wildcard_winners = []
    data['wildcard_games'] = []
    for prediction in predictions.Predictor().predict(wildcard_games(seeds)):
        data['wildcard_games'].append(prediction)
        wildcard_winners.append(prediction.winner)

    divisional_winners = []
    data['divisional_games'] = []
    for prediction in predictions.Predictor().predict(divisional_games(seeds, wildcard_winners)):
        data['divisional_games'].append(prediction)
        divisional_winners.append(prediction.winner)

    data['conference_game'] = predictions.Predictor().predict([conference_game(seeds, divisional_winners)])[0]
    return data

data = {}
conferences = ['afc', 'nfc']

for conference in conferences:
    data[conference] = predict(conference)

print('Seeds')
print('------------------')
for conference in conferences:
    print(conference.upper())

    index = 0
    for seed in data[conference]['seeds']:
        index = index + 1
        print(str(index) + ' ' + seed.name)

    print()

print('Wildcard Games')
print('------------------')
for prediction in data['afc']['wildcard_games'] + data['nfc']['wildcard_games']:
    print(prediction)
    print()

print('Divisional Games')
print('------------------')
for prediction in data['afc']['divisional_games'] + data['nfc']['divisional_games']:
    print(prediction)
    print()

print('Conference Games')
print('------------------')
for prediction in [data['afc']['conference_game'], data['nfc']['conference_game']]:
    print(prediction)
    print()


print('Superbowl')
print('------------------')
print(predictions.Predictor().predict([game(data['afc']['conference_game'].winner, data['nfc']['conference_game'].winner)])[0])

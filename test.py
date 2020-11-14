import sys
import json
import pandas
import datetime
import operator
import numpy

import requests
import sportsreference.nfl.teams
import sportsreference.nfl.boxscore

_teams_by_id = {
    'buf': {'name': 'Bills', 'location': 'Buffalo', 'conference': 'AFC', 'division': 'East'},
    'mia': {'name': 'Dolphins', 'location': 'Miami', 'conference': 'AFC', 'division': 'East'},
    'nwe': {'name': 'Patriots', 'location': 'New England', 'conference': 'AFC', 'division': 'East'},
    'nyj': {'name': 'Jets', 'location': 'New York', 'conference': 'AFC', 'division': 'East'},
    'pit': {'name': 'Steelers', 'location': 'Pittsburgh', 'conference': 'AFC', 'division': 'North'},
    'rav': {'name': 'Ravens', 'location': 'Baltimore', 'conference': 'AFC', 'division': 'North'},
    'cle': {'name': 'Browns', 'location': 'Cleveland', 'conference': 'AFC', 'division': 'North'},
    'cin': {'name': 'Bengals', 'location': 'Cincinnati', 'conference': 'AFC', 'division': 'North'},
    'oti': {'name': 'Titans', 'location': 'Tennessee', 'conference': 'AFC', 'division': 'South'},
    'clt': {'name': 'Colts', 'location': 'Indianapolis', 'conference': 'AFC', 'division': 'South'},
    'jax': {'name': 'Texans', 'location': 'Houston', 'conference': 'AFC', 'division': 'South'},
    'htx': {'name': 'Jaguars', 'location': 'Jacksonville', 'conference': 'AFC', 'division': 'South'},
    'kan': {'name': 'Chiefs', 'location': 'Kansas City', 'conference': 'AFC', 'division': 'West'},
    'rai': {'name': 'Raiders', 'location': 'Las Vegas', 'conference': 'AFC', 'division': 'West'},
    'den': {'name': 'Broncos', 'location': 'Denver', 'conference': 'AFC', 'division': 'West'},
    'sdg': {'name': 'Chargers', 'location': 'Los Angeles', 'conference': 'AFC', 'division': 'West'},
    'phi': {'name': 'Eagles', 'location': 'Philadelphia', 'conference': 'NFC', 'division': 'East'},
    'was': {'name': 'Football Team', 'location': 'Washington', 'conference': 'NFC', 'division': 'East'},
    'dal': {'name': 'Cowboys', 'location': 'Dallas', 'conference': 'NFC', 'division': 'East'},
    'nyg': {'name': 'Giants', 'location': 'New York', 'conference': 'NFC', 'division': 'East'},
    'gnb': {'name': 'Packers', 'location': 'Green Bay', 'conference': 'NFC', 'division': 'North'},
    'chi': {'name': 'Bears', 'location': 'Chicago', 'conference': 'NFC', 'division': 'North'},
    'det': {'name': 'Lions', 'location': 'Detroit', 'conference': 'NFC', 'division': 'North'},
    'min': {'name': 'Vikings', 'location': 'Minnesota', 'conference': 'NFC', 'division': 'North'},
    'tam': {'name': 'Buccaneers', 'location': 'Tampa Bay', 'conference': 'NFC', 'division': 'South'},
    'nor': {'name': 'Saints', 'location': 'New Orleans', 'conference': 'NFC', 'division': 'South'},
    'car': {'name': 'Panthers', 'location': 'Carolina', 'conference': 'NFC', 'division': 'South'},
    'atl': {'name': 'Falcons', 'location': 'Atlanta', 'conference': 'NFC', 'division': 'South'},
    'sea': {'name': 'Seahawks', 'location': 'Seattle', 'conference': 'NFC', 'division': 'West'},
    'crd': {'name': 'Cardinals', 'location': 'Arizona', 'conference': 'NFC', 'division': 'West'},
    'ram': {'name': 'Rams', 'location': 'Los Angeles', 'conference': 'NFC', 'division': 'West'},
    'sfo': {'name': '49ers', 'location': 'San Francisco', 'conference': 'NFC', 'division': 'West'}
}

_teams_by_name = {}
for _id in _teams_by_id:
    _teams_by_name[_teams_by_id[_id]['location'] + ' ' + _teams_by_id[_id]['name']] = {**_teams_by_id[_id], **{'id': _id}}


sportsreference.nfl.teams.Team.id = property(lambda self: self._abbreviation.lower())
sportsreference.nfl.teams.Team.name = property(lambda self: _teams_by_id[self.id]['name'])
sportsreference.nfl.teams.Team.location = property(lambda self: _teams_by_id[self.id]['location'])
sportsreference.nfl.teams.Team.conference = property(lambda self: _teams_by_id[self.id]['conference'])
sportsreference.nfl.teams.Team.division = property(lambda self: _teams_by_id[self.id]['division'])
sportsreference.nfl.teams.Team.fullname = property(lambda self: self.location + ' ' + self.name)
sportsreference.nfl.teams.Team.power = property(lambda self: int((self.win_percentage * 100) + (self.win_percentage * self.strength_of_schedule * self.games_played)))
sportsreference.nfl.teams.Team.expected_win_ratio = property(lambda self: 1 / (1 + ((self.points_against / self.points_for) ** 2)))

teams = sportsreference.nfl.teams.Teams()

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

class Game:
    def __init__(self, season, week, date, time, day, home, away):
        self.away = teams(_teams_by_name[away]['id'])
        self.home = teams(_teams_by_name[home]['id'])
        self.name = self.away.fullname + ' @ ' + self.home.fullname
        self.date = datetime.datetime.strptime(date + ' ' + (str(int(season) + 1) if 'January' in date or 'Feburary' in date else season) + ' ' + time, '%B %d %Y %I:%M%p')
        self.day = day

        self.odds = None
        if self.away.fullname + ' @ ' + self.home.fullname in _odds_by_game:
            self.odds = _odds_by_game[self.name]
        else:
            self.odds = {'spread': {self.home.name : '0', self.away.name: '0'}, 'moneyline': {self.home.name : {'decimal': 0, 'american': '+0'}, self.away.name: {'decimal': 0, 'american': '+0'}}}

        self.boxscore = None
        self.winner = None
        self.finished = False

        if self.date < datetime.datetime.now():
            self.boxscore = sportsreference.nfl.boxscore.Boxscore(self.date.strftime('%Y%m%d0') + self.home.id.lower())
            if self.boxscore.home_abbreviation == 'None':
                self.boxscore = sportsreference.nfl.boxscore.Boxscore(self.date.strftime('%Y%m%d0') + self.away.id.lower())

            try:
                self.winner = self.home if self.boxscore.winner == 'Home' else self.away
                self.finished = True
            except:
                pass

class Pick:
    def __init__(self, game, type, winner):
        self.game = game
        self.type = type
        self.winner = winner
        self.loser = game.home if game.home.name != winner.name else game.away

    def __str__(self):
        return (self.game.away.name.ljust(13) + ' @ ' + self.game.home.name.ljust(13)) + ' --> ' + self.winner.name

class Picks:
    def __init__(self, name, selections):
        self.name = name
        self.selections = selections

    def __iter__(self):
        return self.selections.__iter__()

    def __str__(self):
        string = self.name + '\n---------------------------------\n'
        for pick in self.selections:
            string = string + str(pick) + '\n'

        return string

class PicksGenerator:
    def __init__(self):
        self.name = ""

    def picks(self, games):
        return Picks(self.name, list(map(lambda game: Pick(game, 'moneyline', self.pick(game)), games)))

    def pick(self, game):
        return game.home


class SimpleComparisonPicksGenerator(PicksGenerator):
    def pick(self, game):
        return game.home if self.operator(getattr(game.home, self.property), getattr(game.away, self.property)) else game.away

class BetterWinPercentagePicksGenerator(SimpleComparisonPicksGenerator):
    def __init__(self):
        self.name = "Better Record"
        self.property = "win_percentage"
        self.operator = operator.ge

class BetterSimpleRatingPicksGenerator(SimpleComparisonPicksGenerator):
    def __init__(self):
        self.name = "Better Simple Rating"
        self.property = "simple_rating_system"
        self.operator = operator.ge

class BetterPowerRatingPicksGenerator(SimpleComparisonPicksGenerator):
    def __init__(self):
        self.name = "Better Power Rating"
        self.property = "power"
        self.operator = operator.ge

class BetterPointsScoredRankingPicksGenerator(SimpleComparisonPicksGenerator):
    def __init__(self):
        self.name = "Better Points Scored Ranking"
        self.property = "rank"
        self.operator = operator.lt

class BetterStrengthOfSchedulePicksGenerator(SimpleComparisonPicksGenerator):
    def __init__(self):
        self.name = "Better Strength of Schedule"
        self.property = "rank"
        self.operator = operator.ge

class BetterPointsDifferencePicksGenerator(SimpleComparisonPicksGenerator):
    def __init__(self):
        self.name = "Better Points Difference"
        self.property = "points_difference"
        self.operator = operator.ge

class BetterOddsPicksGenerator(SimpleComparisonPicksGenerator):
    def __init__(self):
        self.name = "Better Odds"

    def pick(self, game):
        try:
            return game.home if int(game.odds['moneyline'][game.home.name]['american']) < 0 else game.away
        except:
            print('WARNING: No moneyline odds for game:', game.name)
            return game.home

class UpsetPicksGenerator(BetterOddsPicksGenerator):
    def __init__(self):
        self.name = 'Better Odds With Upsets'

    def picks(self, games):
        return Picks(self.name, list(map(lambda pick: pick if _is_possible_upset(pick) == False else _swap_winner(pick), super().picks(games))))

class ParlayGenerator:
    def __init__(self):
        self.name = ''

    def parlays(self, picks):
        return [Parlay(picks.name if self.name == '' else picks.name + ' - ' + self.name, 'moneyline', [pick for pick in map(lambda pick: self.process(pick), picks) if pick])]

    def process(self, pick):
        return pick

class FilteringParlayGenerator(ParlayGenerator):
    def process(self, pick):
        return pick if self.filter(pick) == False else None

    def filter(self, pick):
        return False

class AllPicksParlayGenerator(FilteringParlayGenerator):
    pass

class OnlySundayGamesParlayGenerator(FilteringParlayGenerator):
    def __init__(self):
        self.name = 'Only Sunday Games'

    def filter(self, pick):
        return pick.game.day != 'Sun'

class OnlyHomeTeamParlayGenerator(FilteringParlayGenerator):
    def __init__(self):
        self.name = 'Only Home Teams'

    def filter(self, pick):
        return pick.winner.name == pick.game.away.name

class OnlyAwayTeamParlayGenerator(FilteringParlayGenerator):
    def __init__(self):
        self.name = 'Only Away Teams'

    def filter(self, pick):
        return pick.winner.name == pick.game.home.name

class OnlyInterdivisonalGamesParlayGenerator(FilteringParlayGenerator):
    def __init__(self):
        self.name = 'Only Interdivisonal Games'

    def filter(self, pick):
        return pick.game.away.division == pick.game.home.division

class OnlyLargerThanPointSpreads(FilteringParlayGenerator):
        def __init__(self, spread):
            self.name = 'Larger than ' + str(spread) + ' Point Spreads'
            self.spread = spread

        def filter(self, pick):
            try:
                return abs(float(pick.game.odds['spread'][pick.game.home.name])) < self.spread
            except:
                return True

class OnlyLargerThan14PointSpreads(OnlyLargerThanPointSpreads):
    def __init__(self):
        super().__init__(14)

class OnlyLargerThan10PointSpreads(OnlyLargerThanPointSpreads):
    def __init__(self):
        super().__init__(10)

class OnlyLargerThan7PointSpreads(OnlyLargerThanPointSpreads):
    def __init__(self):
        super().__init__(7)

class OnlyLargerThan5PointSpreads(OnlyLargerThanPointSpreads):
    def __init__(self):
        super().__init__(5)

class OnlyLargerThan3PointSpreads(OnlyLargerThanPointSpreads):
    def __init__(self):
        super().__init__(3)

class Parlay:
    def __init__(self, name, type, picks):
        self.name = name
        self.type = type
        self.picks = picks
        self.finished = list(map(lambda pick: pick.game.finished, picks)).count(False) == 0
        self.odds = {'decimal': 1}
        for pick in self.picks:
            if 'moneyline' in pick.game.odds and pick.game.odds['moneyline'][pick.winner.name]['decimal'] != 0.0:
                self.odds['decimal'] = self.odds['decimal'] * pick.game.odds['moneyline'][pick.winner.name]['decimal']

        if self.odds['decimal'] > 0:
            self.odds['american'] = int((self.odds['decimal'] - 1) * 100)
        else:
            self.odds['american'] = int(-100 / (self.odds['decimal'] - 1))


    def __str__(self):
        string = self.name + '\n---------------------------------\n'
        for pick in self.picks:
            string = string + str(pick) + '\n'

        return string

    def __iter__(self):
        return self.picks.__iter__()

def _upset_chances(pick):
    indicators = [pick.winner.simple_rating_system - pick.loser.simple_rating_system, pick.winner.power - pick.loser.power, pick.loser.rank - pick.winner.rank]
    return round(list(map(lambda value: value < 0, indicators)).count(True) / len(indicators) * 100, 1)

def _is_possible_upset(pick):
    return False if _upset_chances(pick) < 66 else True

def _swap_winner(pick):
    pick.winner = pick.game.away if pick.winner.name == pick.game.home.name else pick.game.home
    return pick

if len(sys.argv) >= 2:
    week = sys.argv[1]
else:
    week = '8'

schedule = pandas.read_html('https://www.pro-football-reference.com/years/2020/games.htm')[0]
schedule['season'] = '2020'
schedule['week'] = schedule.iloc[:, 0]
schedule['day']  = schedule.iloc[:, 1]
schedule['date'] = schedule.iloc[:, 2]
schedule['time'] = schedule.iloc[:, 3]
schedule['away'] = numpy.where(schedule.iloc[:, 7].eq('preview') | (schedule.iloc[:, 7].eq('boxscore') & schedule.iloc[:, 5].eq('@')), schedule.iloc[:, 4], schedule.iloc[:, 6])
schedule['home'] = numpy.where(schedule.iloc[:, 7].eq('preview') | (schedule.iloc[:, 7].eq('boxscore') & schedule.iloc[:, 5].eq('@')), schedule.iloc[:, 6], schedule.iloc[:, 4])

#print(sys.argv)


#print(week)
#print(schedule[schedule.Week == week].loc[:,['season', 'week', 'day', 'date', 'time', 'home', 'away']])

games = [Game(**kwargs) for kwargs in schedule[schedule.Week == week].loc[:,['season', 'week', 'date', 'time', 'day', 'away', 'home']].to_dict(orient='records')]
#for game in games:
#    print(game.away.name, '[' + str(game.boxscore.away_points) + ']' if game.odds == None else '[' + game.odds['spread'][game.away.name] + ']', 'at', game.home.name, '[' + str(game.boxscore.home_points) + ']' if game.odds == None else '[' + game.odds['spread'][game.home.name] + ']')


#for game in games:
#    print(game.away.name, str(game.away.wins) + '-' + str(game.away.losses), game.away.win_percentage, game.away.simple_rating_system, game.away.strength_of_schedule, game.away.power)

#print('---------------------')
#for team in sorted(teams, key=lambda x: x.power, reverse=True):
#    print(team.name, team.power)

pickers = [BetterWinPercentagePicksGenerator, BetterSimpleRatingPicksGenerator, BetterPowerRatingPicksGenerator, BetterStrengthOfSchedulePicksGenerator, BetterPointsDifferencePicksGenerator, BetterOddsPicksGenerator, UpsetPicksGenerator]
parlayers = [AllPicksParlayGenerator, OnlyHomeTeamParlayGenerator, OnlyAwayTeamParlayGenerator, OnlyInterdivisonalGamesParlayGenerator, OnlySundayGamesParlayGenerator, OnlyLargerThan14PointSpreads, OnlyLargerThan10PointSpreads, OnlyLargerThan7PointSpreads, OnlyLargerThan5PointSpreads, OnlyLargerThan3PointSpreads]

parlays = []
for picks in list(map(lambda picker: picker().picks(games), pickers)):
    for parlayer in parlayers:
        parlays = parlays + parlayer().parlays(picks)

_picks_per_team = {}
for game in games:
    _picks_per_team[game.home.name] = []
    _picks_per_team[game.away.name] = []

total = 0
for parlay in parlays:
    if len(parlay.picks) > 0:
        print('=========================================================')
        print(parlay.name)
        print('=========================================================')
        correct = 0
        for pick in parlay:
            if 'moneyline' in pick.game.odds:
                print(str(pick).ljust(48), pick.game.odds['moneyline'][pick.winner.name]['american'] if pick.game.finished == False else '[correct]' if pick.winner == pick.game.winner else '[incorrect]')

            _picks_per_team[pick.winner.name].append(parlay)
            if pick.winner == pick.game.winner:
                correct = correct + 1

        print('---------------------------------------------------------')
        if parlay.finished:
            print('Results:', correct, 'out of', len(parlay.picks))
        else:
            print('Odds: ' + str(round(parlay.odds['decimal'], 2)))
            print('Bet: $1.00 - Returns:', '$' + str(round(parlay.odds['decimal'], 2)))
            total = total + round(parlay.odds['decimal'], 2)

        print()

print('Total investment: $' + str(len(parlays)) + '.00')
print('Total possible winnings:', '$' + str(round(total, 2)))
print()


for team in teams:
    if team.name in _picks_per_team:
        print(team.name.ljust(14), (str(len(_picks_per_team[team.name])).rjust(len(str(len(parlays)))) + '/' + str(len(parlays))).ljust(6), '  $' + (str(int(sum(list(map(lambda pick: pick.odds['decimal'], _picks_per_team[team.name])))))).rjust(7)) #, _picks_per_team[team.name])

#def fractional_odds_to_percentage(odds):
#    return 50 if odds == 'Evens' else (1 / (int(odds.split('/')[0]) / int(odds.split('/')[1]) + 1)) * 100

#print()
#for game in games:
#    home_chances = fractional_odds_to_percentage(game.odds['moneyline'][game.home.name]['fractional'])
#    away_chances = fractional_odds_to_percentage(game.odds['moneyline'][game.away.name]['fractional'])

#    home_dutch = (home_chances / (home_chances + away_chances))
#    away_dutch = (away_chances / (home_chances + away_chances))
#    print(game.name, home_dutch + away_dutch)
#    if home_dutch + away_dutch > 1:
#        print(' ', game.home.name + ' wager $' + str(round(home_dutch, 2)), '/', game.away.name + ' wager $' + str(round(away_dutch, 2)))

print()
print('Upsets')
print('------------------------------------')
for pick in BetterOddsPicksGenerator().picks(games):
    if _is_possible_upset(pick):
        print(pick.game.home.name if pick.winner.name != pick.game.home.name else pick.game.away.name, '[' + pick.game.odds['spread'][pick.loser.name] + ' points] will upset', pick.game.home.name if pick.winner.name == pick.game.home.name else pick.game.away.name, '[Bet: $10 (moneyline), Win: $' + str(pick.game.odds['moneyline'][pick.loser.name]['decimal'] * 10) + ']')


print()
print()
sos_offset = abs(min(list(map(lambda team: team.strength_of_schedule, teams))))
#for team in teams:
#    print(team.name.ljust(14), ('asos=' + str(round(team.strength_of_schedule + sos_offset + 1, 1))).ljust(14), ('power=' + str(team.power)).ljust(14), ('rank=' + str(team.rank)).ljust(14), ('expected wins=' + str(team.expected_win_ratio * team.wins)).ljust(14))

print()
print()

for team in sorted(teams, key=lambda team: team.wins + (team.strength_of_schedule + team.wins), reverse=True):
    print(team.name.ljust(14), team.wins + (team.strength_of_schedule + team.wins), team.wins)

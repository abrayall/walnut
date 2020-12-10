import json
import requests
import operator

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
            return game.home if int(getOdds(game)['moneyline'][game.home.name]['american']) < 0 else game.away
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
            if getOdds(pick.game) != None and 'moneyline' in getOdds(pick.game) and getOdds(pick.game)['moneyline'][pick.winner.name]['decimal'] != 0.0:
                self.odds['decimal'] = self.odds['decimal'] * getOdds(pick.game)['moneyline'][pick.winner.name]['decimal']

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
        elif offer['label'] == "Total Points":
            _odds_by_game[event['name']]['points'] = {}
            for i in [0, 1]:
                _odds_by_game[event['name']]['points'][offer['outcomes'][i]['label'].lower()] = {'value': offer['outcomes'][i]['line'], 'american': offer['outcomes'][i]['oddsAmerican'], 'decimal': offer['outcomes'][i]['oddsDecimal'], 'fractional': offer['outcomes'][i]['oddsFractional']}

pickers = [BetterWinPercentagePicksGenerator, BetterSimpleRatingPicksGenerator, BetterPowerRatingPicksGenerator, BetterStrengthOfSchedulePicksGenerator, BetterPointsDifferencePicksGenerator, BetterOddsPicksGenerator, UpsetPicksGenerator]
parlayers = [AllPicksParlayGenerator, OnlyHomeTeamParlayGenerator, OnlyAwayTeamParlayGenerator, OnlyInterdivisonalGamesParlayGenerator, OnlySundayGamesParlayGenerator, OnlyLargerThan14PointSpreads, OnlyLargerThan10PointSpreads, OnlyLargerThan7PointSpreads, OnlyLargerThan5PointSpreads, OnlyLargerThan3PointSpreads]

def getOdds(game):
    return _odds_by_game.get(str(game), None)

def parlays(games):
    parlays = []
    for picks in list(map(lambda picker: picker().picks(games), pickers)):
        for parlayer in parlayers:
            parlays = parlays + parlayer().parlays(picks)

    return parlays

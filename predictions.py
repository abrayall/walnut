import nfl
import betting

import sys
import pandas

#print(pandas.read_html('https://www.teamrankings.com/nfl/')[0])
#print(pandas.read_html('https://www.teamrankings.com/nfl/ranking/predictive-by-other/')[0])

#tables = pandas.read_html('https://www.teamrankings.com/nfl/matchup/jaguars-packers-week-10-2020/stats')
#print(tables[0][tables[0].iloc[:, 0] == 'Points/Game'].iloc[0, 1].replace('(', '').replace(')', '').replace('#', '').split(' '))

#print(pandas.read_html('https://sports.yahoo.com/nfl/standings/'))
#print(pandas.read_html('https://sports.yahoo.com/nfl/standings/?selectedTab=2'))


_teams = {
    'Packers' : 'Green Bay',
    'Chargers' : 'LA Chargers',
    'Steelers' : 'Pittsburgh',
    'Bengals' : 'Cincinnati',
    'Rams' : 'LA Rams',
    'Raiders' : 'Las Vegas',
    '49ers' : 'San Francisco',
    'Saints' : 'New Orleans',
    'Colts' : 'Indianapolis',
    'Falcons' : 'Atlanta',
    'Ravens' : 'Baltimore',
    'Panthers' : 'Carolina',
    'Bills' : 'Buffalo',
    'Patriots' : 'New England',
    'Football Team' : 'Washington',
    'Dolphins' : 'Miami',
    'Bears' : 'Chicago',
    'Browns' : 'Cleveland',
    'Seahawks': 'Seattle',
    'Chiefs' : 'Kansas City',
    'Buccaneers' : 'Tampa Bay',
    'Giants' : 'NY Giants',
    'Vikings' : 'Minnesota',
    'Eagles' : 'Philadelphia',
    'Broncos' : 'Denver',
    'Cardinals' : 'Arizona',
    'Lions' : 'Detroit',
    'Titans' : 'Tennessee',
    'Cowboys' : 'Dallas',
    'Jaguars' : 'Jacksonville',
    'Texans' : 'Houston',
    'Jets' : 'NY Jets'
}

class Predictor:

    def __init__(self, seconds_per_play = 30):
        self.seconds_per_play = seconds_per_play

    def _dataframe(self, url):
        return pandas.read_html(url)[0]

    def _percent(self, data, column):
        data['percent'] = data.iloc[:, column].str.replace('%', '').astype(float)
        return data

    def _mean(self, data, column):
        data['avg'] = data.iloc[:, column].mean()
        return data

    def _adjusted(self, data, column):
        data['adjusted'] = data.iloc[:, column] - data['avg']
        return data

    def predict(self, games):
        offense = self._adjusted(self._mean(self._dataframe('https://www.teamrankings.com/nfl/stat/points-per-play'), 2), 2)
        defense = self._adjusted(self._mean(self._dataframe('https://www.teamrankings.com/nfl/stat/opponent-points-per-play'), 2), 2)

        posession = self._percent(self._dataframe('https://www.teamrankings.com/nfl/stat/time-of-possession-pct-net-of-ot'), 2)
        posession['opponent'] = 100 - posession.iloc[:, 8]
        posession = self._adjusted(self._mean(posession, 9), 9)

        predictions = []
        for game in games:
            home_possesion = posession[posession.Team == _teams.get(game.home.name)].iloc[0]
            away_possesion = posession[posession.Team == _teams.get(game.away.name)].iloc[0]

            home_offense = offense[offense.Team == _teams.get(game.home.name)].iloc[0]
            away_offense = offense[offense.Team == _teams.get(game.away.name)].iloc[0]

            home_defense = defense[defense.Team == _teams.get(game.home.name)].iloc[0]
            away_defense = defense[defense.Team == _teams.get(game.away.name)].iloc[0]

            away_points_per_play = away_offense['2020'] + home_defense['adjusted']
            home_points_per_play = home_offense['2020'] + away_defense['adjusted']
            #print(game.away, 'points per play', away_offense['2020'], '=>', away_points_per_play)
            #print(game.home, 'points per play', home_offense['2020'], '=>', home_points_per_play)

            away_play_count = (((away_possesion['percent'] + home_possesion['adjusted']) / 100) * 3600) / self.seconds_per_play
            home_play_count = (((home_possesion['percent'] + away_possesion['adjusted']) / 100) * 3600) / self.seconds_per_play

            away_score = int(round(away_play_count * away_points_per_play, 0))
            home_score = int(round(home_play_count * home_points_per_play, 0))

            odds = betting.getOdds(game)
            if odds == None:
                odds = {'spread': {game.home.name: '0.0', game.away.name: '0.0'}}

            predictions.append(Prediction(game, home_score, away_score, odds))

        return predictions

class Prediction:
    def __init__(self, game, home_score, away_score, odds):
        self.game = game
        self.home_score = home_score
        self.away_score = away_score
        self.odds = odds

    def __str__(self):
        string = self.game.away.name.ljust(14) + ' ' + str(self.away_score)  + ' ' +  (('[-' + str(abs(self.away_score - self.home_score)) + ' / ' + str(round(float(self.odds['spread'][self.game.away.name]), 1)) + ']') if self.away_score > self.home_score else '') + '\n'
        return string + self.game.home.name.ljust(14)  + ' ' +  str(self.home_score) + ' ' +  (('[-' + str(abs(self.home_score - self.away_score)) + ' / ' + str(round(float(self.odds['spread'][self.game.home.name]), 1)) + ']') if self.home_score > self.away_score else '')

week = nfl.getWeek() if len(sys.argv) != 2 else sys.argv[1]

if __name__ == '__main__':
    print('Week ' + week + ' Predictions')
    print('----------------------')
    for prediction in Predictor().predict(nfl.getGames(week=week)):
        print(prediction)
        print()

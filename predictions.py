import nfl
import betting

import sys
import pandas
import datetime

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

    def __init__(self, seconds_per_play = 24):
        self.seconds_per_play = seconds_per_play

    def _dataframe(self, url):
        return pandas.read_html(url)[0]

    def _normalize(self, data, column, alternative):
        if column in data:
            return data

        return data.rename(columns={alternative: column})

    def _percent(self, data, column):
        data['percent'] = data.iloc[:, column].str.replace('%', '').astype(float)
        return data

    def _mean(self, data, column):
        data['avg'] = data.iloc[:, column].mean()
        return data

    def _adjusted(self, data, column):
        data['adjusted'] = data.iloc[:, column] - data['avg']
        return data

    def _season(self, season, week):
        if int(week) == 1:
            return str(int(season) - 1)
        elif int(week) < 3:
            return 'Last 3'
        else:
            return season

    def predict(self, games):
        date = (games[0].date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        week = games[0].week
        season = nfl.getSeason(date=games[0].date)

        offense_points_per_play = self._adjusted(self._mean(self._normalize(self._dataframe('https://www.teamrankings.com/nfl/stat/points-per-play?date=' + date), season, self._season(season, week)), 2), 2)
        defense_points_per_play = self._adjusted(self._mean(self._normalize(self._dataframe('https://www.teamrankings.com/nfl/stat/opponent-points-per-play?date=' + date), season, self._season(season, week)), 2), 2)

        offense_plays_per_game = self._adjusted(self._mean(self._normalize(self._dataframe('https://www.teamrankings.com/nfl/stat/plays-per-game?date=' + date), season, self._season(season, week)), 2), 2)
        defense_plays_per_game = self._adjusted(self._mean(self._normalize(self._dataframe('https://www.teamrankings.com/nfl/stat/opponent-plays-per-game?date=' + date), season, self._season(season, week)), 2), 2)

        posession = self._percent(self._normalize(self._dataframe('https://www.teamrankings.com/nfl/stat/time-of-possession-pct-net-of-ot?date=' + date), season, self._season(season, week)), 2)
        posession['opponent'] = 100 - posession.iloc[:, 8]
        posession = self._adjusted(self._mean(posession, 9), 9)

        predictions = []
        for game in games:
            home_possesion = posession[posession.Team == _teams.get(game.home.name)].iloc[0]
            away_possesion = posession[posession.Team == _teams.get(game.away.name)].iloc[0]

            home_offense_points_per_play = offense_points_per_play[offense_points_per_play.Team == _teams.get(game.home.name)].iloc[0]
            away_offense_points_per_play = offense_points_per_play[offense_points_per_play.Team == _teams.get(game.away.name)].iloc[0]

            home_defense_points_per_play = defense_points_per_play[defense_points_per_play.Team == _teams.get(game.home.name)].iloc[0]
            away_defense_points_per_play = defense_points_per_play[defense_points_per_play.Team == _teams.get(game.away.name)].iloc[0]

            away_points_per_play = away_offense_points_per_play[season] + home_defense_points_per_play['adjusted']
            home_points_per_play = home_offense_points_per_play[season] + away_defense_points_per_play['adjusted']

            plays_per_game = (
                offense_plays_per_game[offense_plays_per_game.Team == _teams.get(game.home.name)].iloc[0][season] +
                offense_plays_per_game[offense_plays_per_game.Team == _teams.get(game.away.name)].iloc[0][season] +
                defense_plays_per_game[defense_plays_per_game.Team == _teams.get(game.home.name)].iloc[0][season] +
                defense_plays_per_game[defense_plays_per_game.Team == _teams.get(game.away.name)].iloc[0][season]
            ) / 2

            seconds_per_play = (60 * 60) / int(plays_per_game)

            away_play_count = (((away_possesion['percent'] + home_possesion['adjusted']) / 100) * 3600) / seconds_per_play
            home_play_count = (((home_possesion['percent'] + away_possesion['adjusted']) / 100) * 3600) / seconds_per_play

            away_score = round(away_play_count * away_points_per_play, 1)
            home_score = round(home_play_count * home_points_per_play, 1)

            if away_score < 0:
                away_score = 0

            if home_score < 0:
                home_score = 0

            if home_score == away_score:
                home_score = home_score + 1

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
        self.winner = self.game.home if self.home_score >= self.away_score else self.game.away
        self.loser = self.game.home if self.home_score < self.away_score else self.game.away

    def __str__(self):
        if self.game.finished == False:
            #total = float(self.odds['points']['over']['value'].replace('+', ''))
            #print((total / 2) + (float(self.odds['spread'][self.game.away.name]) / 2), (total / 2) - (float(self.odds['spread'][self.game.away.name]) / 2))
            #string = self.game.away.name.ljust(14) + ' ' + str(self.away_score)  + ' ' +  (('[-' + str(abs(round(self.away_score - self.home_score, 1))) + ' / ' + str(round(float(self.odds['spread'][self.game.away.name]), 1)) + '] [' + str(round(self.away_score + self.home_score, 1)) + ' / ' + str(round(float(self.odds['points']['over']['value'].replace('+', '')), 1)) + ']') if self.away_score > self.home_score else '') + '\n'
            #return string + self.game.home.name.ljust(14)  + ' ' +  str(self.home_score) + ' ' +  (('[-' + str(abs(round(self.home_score - self.away_score, 1))) + ' / ' + str(round(float(self.odds['spread'][self.game.home.name]), 1)) + '] [' + str(round(self.away_score + self.home_score, 1)) + ' / ' + str(round(float(self.odds['points']['over']['value'].replace('+', '')), 1)) + ']') if self.home_score > self.away_score else '')
            string = self.game.away.name.ljust(14) + ' ' + str(self.away_score)  + ' ' +  (('[-' + str(abs(round(self.away_score - self.home_score, 1))) + ' / ' + str(round(float(self.odds['spread'][self.game.away.name]), 1)) + ']') if self.away_score > self.home_score else '') + '\n'
            return string + self.game.home.name.ljust(14)  + ' ' +  str(self.home_score) + ' ' +  (('[-' + str(abs(round(self.home_score - self.away_score, 1))) + ' / ' + str(round(float(self.odds['spread'][self.game.home.name]), 1)) + ']') if self.home_score > self.away_score else '')
        else:
            boxscore = nfl.getBoxscore(self.game)
            string = self.game.away.name.ljust(14) + ' ' + str(self.away_score)  + ' vs ' +  str(boxscore.away_points) + ' [' + str(abs(self.away_score - boxscore.away_points)) + ']\n'
            return string + self.game.home.name.ljust(14)  + ' ' +  str(self.home_score) + ' vs ' +  str(boxscore.home_points) + ' [' + str(abs(self.home_score - boxscore.home_points)) + '] ' + ('CORRECT' if self.winner.name == boxscore.winner.name else '')

week = nfl.getWeek() if len(sys.argv) != 2 else sys.argv[1]

if __name__ == '__main__':
    print('Week ' + week + ' Predictions')
    print('----------------------')
    for prediction in Predictor().predict(nfl.getGames(week=week)):
        print(prediction)
        print()

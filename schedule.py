import pandas
import datetime
import numpy

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

schedule = pandas.read_html('https://www.pro-football-reference.com/years/2020/games.htm')[0]
schedule['season'] = '2020'
schedule['week'] = schedule.iloc[:, 0]
schedule['day']  = schedule.iloc[:, 1]
schedule['date'] = schedule.iloc[:, 2]
schedule['time'] = schedule.iloc[:, 3]
schedule['away'] = numpy.where(schedule.iloc[:, 7].eq('preview') | (schedule.iloc[:, 7].eq('boxscore') & schedule.iloc[:, 5].eq('@')), schedule.iloc[:, 4], schedule.iloc[:, 6])
schedule['home'] = numpy.where(schedule.iloc[:, 7].eq('preview') | (schedule.iloc[:, 7].eq('boxscore') & schedule.iloc[:, 5].eq('@')), schedule.iloc[:, 6], schedule.iloc[:, 4])

print(schedule)

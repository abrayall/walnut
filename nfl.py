import numpy
import pandas
import datetime

import requests
from bs4 import BeautifulSoup

import sportsreference.nfl.teams
import sportsreference.nfl.boxscore

_conferences = [
    {'id': 'afc', 'name': 'AFC', 'fullname': 'American Football Conference'},
    {'id': 'nfc', 'name': 'NFC', 'fullname': 'National Football Conference'}
]

_divisions = [
    {'id': 'afc-north', 'name': 'AFC North', 'conference': 'afc', 'location': 'north'},
    {'id': 'afc-south', 'name': 'AFC South', 'conference': 'afc', 'location': 'south'},
    {'id': 'afc-east', 'name': 'AFC East', 'conference': 'afc', 'location': 'east'},
    {'id': 'afc-west', 'name': 'AFC West', 'conference': 'afc', 'location': 'west'},
    {'id': 'nfc-north', 'name': 'NFC North', 'conference': 'nfc', 'location': 'north'},
    {'id': 'nfc-south', 'name': 'NFC South', 'conference': 'nfc', 'location': 'south'},
    {'id': 'nfc-east', 'name': 'NFC East', 'conference': 'nfc', 'location': 'east'},
    {'id': 'nfc-west', 'name': 'NFC West', 'conference': 'nfc', 'location': 'west'}
]

_teams_by_id = {
    'buf': {'name': 'Bills', 'location': 'Buffalo', 'conference': 'afc', 'division': 'afc-east'},
    'mia': {'name': 'Dolphins', 'location': 'Miami', 'conference': 'afc', 'division': 'afc-east'},
    'nwe': {'name': 'Patriots', 'location': 'New England', 'conference': 'afc', 'division': 'afc-east'},
    'nyj': {'name': 'Jets', 'location': 'New York', 'conference': 'afc', 'division': 'afc-east'},
    'pit': {'name': 'Steelers', 'location': 'Pittsburgh', 'conference': 'afc', 'division': 'afc-north'},
    'rav': {'name': 'Ravens', 'location': 'Baltimore', 'conference': 'afc', 'division': 'afc-north'},
    'cle': {'name': 'Browns', 'location': 'Cleveland', 'conference': 'afc', 'division': 'afc-north'},
    'cin': {'name': 'Bengals', 'location': 'Cincinnati', 'conference': 'afc', 'division': 'afc-north'},
    'oti': {'name': 'Titans', 'location': 'Tennessee', 'conference': 'afc', 'division': 'afc-south'},
    'clt': {'name': 'Colts', 'location': 'Indianapolis', 'conference': 'afc', 'division': 'afc-south'},
    'htx': {'name': 'Texans', 'location': 'Houston', 'conference': 'afc', 'division': 'afc-south'},
    'jax': {'name': 'Jaguars', 'location': 'Jacksonville', 'conference': 'afc', 'division': 'afc-south'},
    'kan': {'name': 'Chiefs', 'location': 'Kansas City', 'conference': 'afc', 'division': 'afc-west'},
    'rai': {'name': 'Raiders', 'location': 'Las Vegas', 'conference': 'afc', 'division': 'afc-west'},
    'den': {'name': 'Broncos', 'location': 'Denver', 'conference': 'afc', 'division': 'afc-west'},
    'sdg': {'name': 'Chargers', 'location': 'Los Angeles', 'conference': 'afc', 'division': 'afc-west'},
    'phi': {'name': 'Eagles', 'location': 'Philadelphia', 'conference': 'nfc', 'division': 'nfc-east'},
    'was': {'name': 'Football Team', 'location': 'Washington', 'conference': 'nfc', 'division': 'nfc-east'},
    'dal': {'name': 'Cowboys', 'location': 'Dallas', 'conference': 'nfc', 'division': 'nfc-east'},
    'nyg': {'name': 'Giants', 'location': 'New York', 'conference': 'nfc', 'division': 'nfc-east'},
    'gnb': {'name': 'Packers', 'location': 'Green Bay', 'conference': 'nfc', 'division': 'nfc-north'},
    'chi': {'name': 'Bears', 'location': 'Chicago', 'conference': 'nfc', 'division': 'nfc-north'},
    'det': {'name': 'Lions', 'location': 'Detroit', 'conference': 'nfc', 'division': 'nfc-north'},
    'min': {'name': 'Vikings', 'location': 'Minnesota', 'conference': 'nfc', 'division': 'nfc-north'},
    'tam': {'name': 'Buccaneers', 'location': 'Tampa Bay', 'conference': 'nfc', 'division': 'nfc-south'},
    'nor': {'name': 'Saints', 'location': 'New Orleans', 'conference': 'nfc', 'division': 'nfc-south'},
    'atl': {'name': 'Falcons', 'location': 'Atlanta', 'conference': 'nfc', 'division': 'nfc-south'},
    'car': {'name': 'Panthers', 'location': 'Carolina', 'conference': 'nfc', 'division': 'nfc-south'},
    'crd': {'name': 'Cardinals', 'location': 'Arizona', 'conference': 'nfc', 'division': 'nfc-west'},
    'sea': {'name': 'Seahawks', 'location': 'Seattle', 'conference': 'nfc', 'division': 'nfc-west'},
    'ram': {'name': 'Rams', 'location': 'Los Angeles', 'conference': 'nfc', 'division': 'nfc-west'},
    'sfo': {'name': '49ers', 'location': 'San Francisco', 'conference': 'nfc', 'division': 'nfc-west'}
}

_teams_by_name = {}
for _id in _teams_by_id:
    _teams_by_name[_teams_by_id[_id]['name']] = {**_teams_by_id[_id], **{'id': _id}}

_teams_by_fullname = {}
for _id in _teams_by_id:
    _teams_by_fullname[_teams_by_id[_id]['location'] + ' ' + _teams_by_id[_id]['name']] = {**_teams_by_id[_id], **{'id': _id}}

_teams = sportsreference.nfl.teams.Teams()
sportsreference.nfl.teams.Team.id = property(lambda self: self._abbreviation.lower())
sportsreference.nfl.teams.Team.name = property(lambda self: _teams_by_id[self.id]['name'])
sportsreference.nfl.teams.Team.location = property(lambda self: _teams_by_id[self.id]['location'])
sportsreference.nfl.teams.Team.conference = property(lambda self: _teams_by_id[self.id]['conference'])
sportsreference.nfl.teams.Team.division = property(lambda self: _teams_by_id[self.id]['division'])
sportsreference.nfl.teams.Team.fullname = property(lambda self: self.location + ' ' + self.name)
sportsreference.nfl.teams.Team.power = property(lambda self: int((self.win_percentage * 100) + (self.win_percentage * self.strength_of_schedule * self.games_played)))
sportsreference.nfl.teams.Team.expected_win_ratio = property(lambda self: 1 / (1 + ((self.points_against / self.points_for) ** 2)))
sportsreference.nfl.teams.Team.__str__ = lambda self: self.fullname

sportsreference.nfl.boxscore.Boxscore.home = property(lambda self: _teams(self.home_abbreviation.lower()))
sportsreference.nfl.boxscore.Boxscore.away = property(lambda self: _teams(self.away_abbreviation.lower()))
sportsreference.nfl.boxscore.Boxscore.winner = property(lambda self: self.home if self.home_points >= self.away_points else self.away)

class Game:
    def __init__(self, season, week, date, time, day, home, away):
        self.away = away if isinstance(away, str) == False else getTeam(away)
        self.home = home if isinstance(home, str) == False else getTeam(home)
        self.name = self.away.fullname + ' @ ' + self.home.fullname
        self.season = season
        self.week = week
        self.date = datetime.datetime.strptime(date + ' ' + (str(int(season) + 1) if 'January' in date or 'Feburary' in date else season) + ' ' + time, '%B %d %Y %I:%M%p')
        self.day = day
        self.finished = True if self.date < datetime.datetime.now() else False

    def __str__(self):
        return self.away.fullname + ' @ ' + self.home.fullname

def getTeam(team=""):
    return _teams(_teams_by_id.get(team, _teams_by_name.get(team, _teams_by_fullname.get(team, None)))['id'])

def getTeams(conference=None, division=None):
    if isinstance(conference, str):
        conference = getConference(conference)

    if isinstance(division, str):
        division = getDivision(division)

    return list(filter(lambda team: ((conference == None or team.conference == conference['id']) and (division == None or team.division == division['id'])), _teams))

def getConferences(self):
    return _conferences

def getConference(id):
    for conference in _conferences:
        if conference['id'] == id.lower():
            return conference

    return None

def getDivisions(conference):
    if isinstance(conference, str):
        conference = getConference(conference)

    return list(filter(lambda division: (conference == None or division['conference'] == conference['id']), _divisions))

def getDivision(id, conference=None):
    if isinstance(conference, str):
        conference = getConference(conference)

    for division in _divisions:
        if ((conference == None or division['conference'] == conference['id']) and (division['id'] == id.lower() or division['location'] == id.lower())):
            return division

    return None

def getSeason(date=None):
    if date == None:
        return str(getSeasons()[0])
    elif date.month > 4:
        return str(date.year)
    else:
        return str(date.year - 1)

def getSeasons():
    return list(pandas.read_html('https://www.pro-football-reference.com/years/')[0].iloc[:, 0])

def getWeek():
    return BeautifulSoup(requests.get('https://www.nfl.com/schedules/').text, 'html.parser').select_one('h2.nfl-c-content-header__roofline').text.split('WEEK ')[1]

def getGames(season=None, week=None):
    if season == None:
        season = getSeason()

    if week == None:
        week = getWeek()

    schedule = pandas.read_html('https://www.pro-football-reference.com/years/' + str(season) + '/games.htm')[0]
    schedule['season'] = str(season)
    schedule['week'] = schedule.iloc[:, 0]
    schedule['day']  = schedule.iloc[:, 1]
    schedule['date'] = schedule.iloc[:, 2]
    schedule['time'] = schedule.iloc[:, 3]
    schedule['away'] = numpy.where(schedule.iloc[:, 7].eq('preview') | (schedule.iloc[:, 7].eq('boxscore') & schedule.iloc[:, 5].eq('@')), schedule.iloc[:, 4], schedule.iloc[:, 6])
    schedule['home'] = numpy.where(schedule.iloc[:, 7].eq('preview') | (schedule.iloc[:, 7].eq('boxscore') & schedule.iloc[:, 5].eq('@')), schedule.iloc[:, 6], schedule.iloc[:, 4])

    return [Game(**kwargs) for kwargs in schedule[schedule.Week == str(week)].loc[:,['season', 'week', 'date', 'time', 'day', 'away', 'home']].to_dict(orient='records')]


def getBoxscore(game):
    boxscore = sportsreference.nfl.boxscore.Boxscore(game.date.strftime('%Y%m%d0') + game.home.id.lower())
    if boxscore.home_abbreviation == 'None':
        boxscore = sportsreference.nfl.boxscore.Boxscore(game.date.strftime('%Y%m%d0') + game.away.id.lower())

    return boxscore

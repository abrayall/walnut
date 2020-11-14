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

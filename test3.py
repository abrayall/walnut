import pandas

print(pandas.read_html('https://www.teamrankings.com/nfl/')[0])
print(pandas.read_html('https://www.teamrankings.com/nfl/ranking/predictive-by-other/')[0])


tables = pandas.read_html('https://www.teamrankings.com/nfl/matchup/jaguars-packers-week-10-2020/stats')
print(tables[0][tables[0].iloc[:, 0] == 'Points/Game'].iloc[0, 1].replace('(', '').replace(')', '').replace('#', '').split(' '))

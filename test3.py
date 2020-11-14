import pandas

print(pandas.read_html('https://www.teamrankings.com/nfl/')[0])


print(pandas.read_html('https://www.teamrankings.com/nfl/ranking/predictive-by-other/')[0])

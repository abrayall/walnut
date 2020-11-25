
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

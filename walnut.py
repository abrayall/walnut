import nfl
import betting

print("Parlays:")
print('------------------------------------')
total = 0
for parlay in betting.parlays(nfl.getGames()):
    if len(parlay.picks) > 0:
        print('=========================================================')
        print(parlay.name)
        print('=========================================================')
        correct = 0
        for pick in parlay:
            if betting.getOdds(pick.game) != None and 'moneyline' in betting.getOdds(pick.game):
                print(str(pick).ljust(48), betting.getOdds(pick.game)['moneyline'][pick.winner.name]['american'] if pick.game.finished == False else '[correct]' if pick.winner == pick.game.winner else '[incorrect]')

            #_picks_per_team[pick.winner.name].append(parlay)
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

print()
print("Upsets")
print('------------------------------------')
for pick in betting.BetterOddsPicksGenerator().picks(nfl.getGames()):
    if betting._is_possible_upset(pick):
        print(pick.game.home.name if pick.winner.name != pick.game.home.name else pick.game.away.name, '[' + betting.getOdds(pick.game)['spread'][pick.loser.name] + ' points] will upset', pick.game.home.name if pick.winner.name == pick.game.home.name else pick.game.away.name, '[Bet: $10 (moneyline), Win: $' + str(betting.getOdds(pick.game)['moneyline'][pick.loser.name]['decimal'] * 10) + ']')

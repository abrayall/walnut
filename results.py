import nfl
import betting
import predictions

import sys

week = nfl.getWeek() if len(sys.argv) != 2 else sys.argv[1]

total = 0
correct = 0
if __name__ == '__main__':
    for week in range(1, 13):
        _total = 0
        _correct = 0
        for prediction in predictions.Predictor().predict(nfl.getGames(week=week)):
            if prediction.game.finished == True:
                boxscore = nfl.getBoxscore(prediction.game)
                #print(prediction.game, boxscore.home_points, boxscore.away_points)
                _total = _total + 1
                if prediction.winner == boxscore.winner:
                    _correct = _correct + 1

        total = total + _total
        correct = correct + _correct
        print('Week', week, ':', _correct, 'of', _total, '[' + str(100 - round(100 * ((_total - _correct) / _total), 1)) + '%]')

print('Total :', correct, 'of', total, '[' + str(100 - round(100 * ((total - correct) / total), 1)) + '%]')

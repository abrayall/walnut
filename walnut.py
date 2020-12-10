import sys

import nfl
import predictions

week = nfl.getWeek() if len(sys.argv) != 2 else sys.argv[1]
if __name__ == '__main__':
    print('Week ' + week + ' Predictions')
    print('----------------------')
    for prediction in predictions.Predictor().predict(nfl.getGames(week=week)):
        print(prediction)
        print()

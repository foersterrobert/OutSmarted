
import numpy as np
import math
# MINIMAX ALGORITHM
def checkForWin(field):
    if (max(field.sum(axis=1)) == 3 or max(field.sum(axis=0)) == 3):
        return 10
    elif (min(field.sum(axis=1)) == -3 or min(field.sum(axis=0)) == -3):
        return -10
    elif (np.trace(field) == 3):
        return 10
    elif (np.trace(field) == -3):
        return -10
    elif (np.trace(np.fliplr(field)) == 3):
        return 10
    elif (np.trace(np.fliplr(field)) == -3):
        return -10
    elif np.count_nonzero(field) == 9:
        return 1000
    return False

def minimax(field, isMaximizing, alpha, beta, probability):
    if checkForWin(field) == 10:
        probability[0] += 1
        return {
            'move': None,
            'score': - 1 * ((9 - np.count_nonzero(field)) + 1),
            'winning_probability': probability
        }
    elif checkForWin(field) == -10:
        probability[1] += 1
        return {
            'move': None,
            'score': 1 * ((9 - np.count_nonzero(field)) + 1),
            'winning_probability': probability
        }
    elif checkForWin(field) == 1000:
        probability[2] += 1
        return {
            'move': None,
            'score': 0,
            'winning_probability': probability
        }
    
    if isMaximizing:
        best = {'move': None, 'score': -math.inf, 'winning_probability': probability}
    elif not isMaximizing:
        best = {'move': None, 'score': math.inf, 'winning_probability': probability}

    for i in range(3):
        for j in range(3):
            if isMaximizing:
                if field[i][j] == 0:
                    field[i][j] = -1
                    sim_score = minimax(field, False, alpha, beta, probability)
                    field[i][j] = 0

                    sim_score['move'] = (i, j)
                    best = max(best, sim_score, key=lambda x: x['score'])
                    alpha = max(alpha, best['score'])
                    if beta <= alpha:
                        break
                    
            elif not isMaximizing:
                if field[i][j] == 0:
                    field[i][j] = 1
                    sim_score = minimax(field, True, alpha, beta, probability)
                    field[i][j] = 0

                    sim_score['move'] = (i, j)
                    best = min(best, sim_score, key=lambda x: x['score'])
                    beta = min(beta, best['score'])
                    if beta <= alpha:
                        break
    return best
def bestMove(field):
    winning_probability = [0, 0, 0]
    if np.count_nonzero(field) != 9:
        if np.count_nonzero(field) == 0:
            move = (0,0)
        else:
            move = minimax(field, True, -math.inf, math.inf, winning_probability)
            winning_probability = move["winning_probability"]
            move = move["move"]
        if move != None:
            field[move[0]][move[1]] = -2
    # winning_probality = [win, lose, draw]
    winning_probability = [round(x / sum(winning_probability), 2) if sum(winning_probability) != 0 else x for x in winning_probability]
    return field, winning_probability
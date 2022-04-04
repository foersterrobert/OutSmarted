import numpy as np
import math
import os

def clear():
    os.system("clear")

#create a numpy array
global field
field = np.array([[0,0,0],[0,0,0],[0,0,0]], dtype=np.int8)
#create a numpy array with the winning combinations
def printfield():
    for i in range(3):
        for j in range(3):
            print(field[i,j], end=" ")
        print()
printfield()

def checkForWin():

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


def minimax(field, isMaximizing):
    if checkForWin() == 10:
        return {
            'move': None,
            'score': - 1 * ((9 - np.count_nonzero(field)) + 1)
        }
    elif checkForWin() == -10:
        return {
            'move': None,
            'score': 1 * ((9 - np.count_nonzero(field)) + 1)
        }
    elif checkForWin() == 1000:
        return {
            'move': None,
            'score': 0
        }
    
    if isMaximizing:
        best = {'move': None, 'score': -math.inf}
    elif not isMaximizing:
        best = {'move': None, 'score': math.inf}

    for i in range(3):
        for j in range(3):
            if isMaximizing:
                if field[i][j] == 0:
                    field[i][j] = -1
                    sim_score = minimax(field, False)
                    field[i][j] = 0

                    sim_score['move'] = (i, j)
                    if sim_score['score'] > best['score']:
                        best = sim_score
            elif not isMaximizing:
                if field[i][j] == 0:
                    field[i][j] = 1
                    sim_score = minimax(field, True)
                    field[i][j] = 0

                    sim_score['move'] = (i, j)
                    if sim_score['score'] < best['score']:
                        best = sim_score
    return best

def bestmove():
    if np.count_nonzero(field) == 0:
        move = (0,0)
    else:
        move = minimax(field, True)['move']
    print(move)
    field[move[0]][move[1]] = -1


def playerinput():
    while True:
        x = int(input("Enter the row: "))
        y = int(input("Enter the column: "))
        if field[x][y] == 0:
            field[x][y] = 1
            break
        else:
            print("Invalid move")
            printfield()
            playerinput()


field = np.array([[0,0,0],[0,0,0],[0,0,0]], dtype=np.int8)
while (checkForWin() == False):
    printfield()
    print("-------------------")
    playerinput()
    clear()
    printfield()
    if checkForWin() == False:
        print("-------------------")
        # field = np.array(eval((input("Enter the entire field:"))), dtype=np.int8)
        bestmove()
        # print(field.tolist())
    else:
        printfield()
        print("-------------------")
if (checkForWin() == 10):
    printfield()
    print("You win!")
elif (checkForWin() == -10):
    printfield()
    print("You Lost!")
elif (checkForWin() == 1000):
    printfield()
    print("Draw!")
else:
    print("Something went wrong")


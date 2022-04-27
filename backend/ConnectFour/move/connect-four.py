import numpy as np
import os
import math

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class connectFour:
    def __init__(self):
        self.board = np.zeros((6, 7))
        self.player = 1
        self.winner = 0
        self.aiplayer = -1
        self.humanplayer = 1
        self.moves = 0
        reward = 0

    def checkwinner(self):
        for i in range(6):
            for j in range(4):
                if self.board[i][j] == self.board[i][j+1] == self.board[i][j+2] == self.board[i][j+3] != 0:
                    self.winner = self.board[i][j]
                    return True

        for i in range(3):
            for j in range(7):
                if self.board[i][j] == self.board[i+1][j] == self.board[i+2][j] == self.board[i+3][j] != 0:
                    self.winner = self.board[i][j]
                    return True

        for i in range(3):
            for j in range(4):
                if self.board[i][j] == self.board[i+1][j+1] == self.board[i+2][j+2] == self.board[i+3][j+3] != 0:
                    self.winner = self.board[i][j]
                    return True

        for i in range(3, 6):
            for j in range(4):
                if self.board[i][j] == self.board[i-1][j+1] == self.board[i-2][j+2] == self.board[i-3][j+3] != 0:
                    self.winner = self.board[i][j]
                    return True
        
        if np.count_nonzero(self.board) == 42:
            return 1000

        return False
    
    """def jespersfunction(self):
        reward = 0
        if self.checkwinner() == True:
            if self.winner == self.humanplayer:
                reward = - 1 #  * (np.count_nonzero(self.board))
            elif self.winner == self.aiplayer:
                reward = 1 * (42 - np.count_nonzero(self.board))
        else:
            reward = 0"""



    def printwinner(self):
        if self.checkwinner() == True:
            if self.winner == 1:
                print("X is the winner!")
            else:
                print("O is the winner!")
            return True
        else:
            return False
    

    def humanplayerinput(self):
        while True:
            x = int(input("Enter the column: "))
            for i in range(5, -1, -1):
                if self.board[0][x] == 0:
                    if self.board[i][x] == 0:
                        self.board[i][x] = self.player
                        self.player = -self.player
                        break
                else:
                    print("Column is full")
                    self.humanplayerinput()
                    break
            break

    def minimax(self, isMaximising, alpha, beta):
        
        if self.checkwinner() == True:
            if self.winner == -1:
                # return {'move': None,'score': - 1 * ((42 - np.count_nonzero(self.board)) + 1)}
                return {'move': None,'score':  1000}
            elif self.winner == 1:
                # return {'move': None,'score': 1 * ((42 - np.count_nonzero(self.board)) + 1)}
                return {'move': None,'score': -1000}
        elif self.checkwinner() == 1000:
            return {'move': None, 'score': 0}
        
        if isMaximising:
            best = {'move': None, 'score': -math.inf}
        elif not isMaximising:
            best = {'move': None, 'score': math.inf}

        for i in range(7):
            for j in range(5, -1, -1):
                if self.board[j][i] == 0:
                    if isMaximising:
                        self.board[j][i] = self.player
                        self.player = -self.player

                        score = self.minimax(False, alpha, beta)
                        self.player = -self.player
                        self.board[j][i] = 0
                        self.winner = 0


                        score["move"] = i
                        best = max(best, score, key=lambda x: x['score'])
                        alpha = max(alpha, best['score'])
                        print(best)
                        if beta <= alpha:
                            break


                    elif not isMaximising:
                        self.board[j][i] = self.player
                        self.player = -self.player

                        score = self.minimax(True, alpha, beta)
                        self.player = -self.player
                        self.board[j][i] = 0
                        self.winner = 0

                        score["move"] = i
                        best = min(best, score, key=lambda x: x['score'])
                        beta = min(beta, best['score'])
                        print(best)
                        if beta <= alpha:
                            break
                break
        return best

        # for i in range(3):
        #     for j in range(3):
        #         if isMaximizing:
        #             if self.board[i][j] == 0:
        #                 self.board[i][j] = -1
        #                 sim_score = self.minimax(self.board, False, alpha, beta)
        #                 self.board[i][j] = 0

        #                 sim_score['move'] = (i, j)
        #                 best = max(best, sim_score, key=lambda x: x['score'])
        #                 alpha = max(alpha, best['score'])
        #                 if beta <= alpha:
        #                     break
                        

        #         elif not isMaximizing:
        #             if self.board[i][j] == 0:
        #                 self.board[i][j] = 1
        #                 sim_score = self.minimax(self.board, True, alpha, beta)
        #                 self.board[i][j] = 0

        #                 sim_score['move'] = (i, j)
        #                 best = min(best, sim_score, key=lambda x: x['score'])
        #                 beta = min(beta, best['score'])
        #                 if beta <= alpha:
        #                     break
        # return best

    def aiplayerinput(self):
        if np.count_nonzero(self.board) == 0:
            move = 0
        else:
            move = self.minimax(True, -math.inf, math.inf)['move']
            
        for i in range(5, -1, -1):
            if self.board[i][move] == 0:
                self.board[i][move] = self.player
                self.player = -self.player
                break



    """def aiplayerinput(self):
        while True:
            x = np.random.randint(0, 7)
            for i in range(5, -1, -1):
                if self.board[0][x] == 0:
                    if self.board[i][x] == 0:
                        self.board[i][x] = self.player
                        self.player = -self.player
                        break
                else:
                    self.aiplayerinput()
                    break
            break"""
    
    def printboard(self):

        print("\n──┬───┬───┬───┬───┬───┬───┐")
        for i in range(6):
            for j in range(7):
                if self.board[i][j] == 1:
                    print("X", end=" │ ")
                elif self.board[i][j] == -1:
                    print("O", end=" │ ")
                else:
                    print(" ", end=" │ ")
            print("\n──┼───┼───┼───┼───┼───┼───┤")
    state = []

if __name__ == "__main__":
    game = connectFour()
    game.printboard()
    while True:
        game.humanplayerinput()
        clear()
        game.printboard()
        if game.checkwinner() == True:
            break
        game.aiplayerinput()
        clear()
        game.printboard()
        if game.checkwinner() == True:
            break
    game.printwinner()
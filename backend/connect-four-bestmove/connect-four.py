import numpy as np
import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class connectFour:
    def __init__(self):
        self.board = np.zeros((6, 8))
        self.player = 1
        self.winner = 0


    def checkwinner(self):
        for i in range(6):
            for j in range(4):
                if self.board[i][j] == self.board[i][j+1] == self.board[i][j+2] == self.board[i][j+3] != 0:
                    self.winner = self.board[i][j]
                    return True

        for i in range(3):
            for j in range(8):
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

        return False



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
                print()
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

    def aiplayerinput(self):
        while True:
            x = np.random.randint(0, 8)
            for i in range(5, -1, -1):
                if self.board[0][x] == 0:
                    if self.board[i][x] == 0:
                        self.board[i][x] = self.player
                        self.player = -self.player
                        break
                else:
                    self.aiplayerinput()
                    break
            break
    
    def printboard(self):

        print("\n──┬───┬───┬───┬───┬───┬───┬───┬")
        for i in range(6):
            for j in range(8):
                if self.board[i][j] == 1:
                    print("X", end=" │ ")
                elif self.board[i][j] == -1:
                    print("O", end=" │ ")
                else:
                    print("-", end=" │ ")
            print("\n──┼───┼───┼───┼───┼───┼───┼───┼")

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
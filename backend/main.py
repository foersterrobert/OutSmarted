import base64
from flask import Flask, jsonify, request
from PIL import Image
from app.Classification import classification as clf
# from Chess.detect import chessDetect
# from Chess.move import chessMove
from app.ConnectFour.detect import connectfourDetect as cfDetect
from app.ConnectFour.move import connectfourMove as cfMove
from app.TicTacToe.detect import tictactoeDetect as tttDetect
from app.TicTacToe.move import tictactoeMove as tttMove
from PIL import Image
import os
import random
import matplotlib.pyplot as plt
plt.switch_backend('agg')

app = Flask(__name__)

# def chessState(image, player):
#     image = np.array(image)
#     state, corners = chessDetect.recognizer.predict(image)
#     if not chessMove.is_terminal(state):
#         state = chessMove.bestMove(state, player)
#     print(state)
#     return state

def connectfourState(image, player, ranNumber="image"):
    try:
        state = cfDetect.detectBoard(image, ranNumber)
        state = state.reshape(7*6).tolist()
    except Exception:
        state = [0] * 42
        image.save(f'{ranNumber}.png')
    if not cfMove.is_terminal(state):
        column = cfMove.mcts(state, player)
        cfMove.drop_piece(state, column, 2*player)
    state = [state[i:i+7] for i in range(0, 42, 7)]
    return state

def tictactoeState(image, player, ranNumber="image"):
    state = tttDetect.detectBoard(image, ranNumber)    
    state *= player
    state, winning_probability = tttMove.bestMove(state)
    winning_probability = winning_probability.tolist()
    winning_probability = [winning_probability[0] * 100, winning_probability[1] * 100, winning_probability[2] * 100]
    state *= player
    return state.astype(int).tolist(), winning_probability

@app.route("/state", methods=['POST'])
def getState():
    ranNumber = str(random.randint(0, 100000000))
    image, game, player = request.files['image'], request.form['game'], request.form['player']

    image = Image.open(image)
    width, height = image.size
    image = image.crop((
        max(0, (width - height) / 2), 
        max(0, (height - width) / 2), 
        width - max(0, (width - height) / 2),
        height - max(0, (height - width) / 2)
    ))

    game, player = int(game), int(player)
    if game == 1:
        state, winning_percentage = tictactoeState(image, player, ranNumber)
    elif game == 2:
        state = connectfourState(image, player, ranNumber)
    # elif game == 3:
    #     state = chessState(image, player)
    else:
        state = []

    with open(f'{ranNumber}.png', 'rb') as f:
        imageJson = base64.b64encode(f.read()).decode('ascii')

    # delete image file
    os.remove(f'{ranNumber}.png')
    return jsonify({'state': state, 'image': imageJson})

@app.route("/game", methods=['POST'])
def getGame():
    image = request.files['image']
    image = Image.open(image)
    width, height = image.size
    image = image.crop((
        max(0, (width - height) / 2), 
        max(0, (height - width) / 2), 
        width - max(0, (width - height) / 2),
        height - max(0, (height - width) / 2)
    ))
    image = image.resize((168, 168), Image.ANTIALIAS)
    image = image.convert('L')
    game, vals = clf.detectGame(image)
    return jsonify({'game': game, 'out': vals})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=30001)

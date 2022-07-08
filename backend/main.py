import base64
from flask import Flask, jsonify, request
from PIL import Image
from Classification import classification as clf
from Chess.detect import chessDetect
from Chess.move import chessMove
from ConnectFour.detect import connectfourDetect as cfDetect
from ConnectFour.move import connectfourMove as cfMove
from TicTacToe.detect import tictactoeDetect as tttDetect
from TicTacToe.move import tictactoeMove as tttMove
from PIL import Image

app = Flask(__name__)

def chessState(image, player):
    state, corners = chessDetect.recognizer.predict(image)
    if not chessMove.is_terminal(state):
        state = chessMove.bestMove(state, player)
    print(state)
    return state

def connectfourState(image, player):
    try:
        state = cfDetect.detectBoard(image)
        state = state.reshape(7*6).tolist()
    except Exception:
        state = [0] * 42
        image.save('image.png')
    if not cfMove.is_terminal(state):
        column = cfMove.mcts(state, player)
        cfMove.drop_piece(state, column, 2*player)
    state = [state[i:i+7] for i in range(0, 42, 7)]
    return state

def tictactoeState(image, player):
    state = tttDetect.detectBoard(image)    
    state *= player
    state = tttMove.bestMove(state)
    state *= player
    return state.astype(int).tolist()

@app.route("/state", methods=['POST'])
def getState():
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
        state = tictactoeState(image, player)
    elif game == 2:
        state = connectfourState(image, player)
    elif game == 3:
        state = chessState(image, player)
    else:
        state = []

    with open('image.png', 'rb') as f:
        imageJson = base64.b64encode(f.read()).decode('ascii')
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
    app.run(host='0.0.0.0')

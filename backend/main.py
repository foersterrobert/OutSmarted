import numpy as np
from flask import Flask, jsonify, request
from PIL import Image
from connectfour import connectFourState
from torchvision.transforms.functional import to_tensor
import tictactoe as ttt
import torch
from PIL import Image
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

def minimax(field, isMaximizing, alpha, beta):
    if checkForWin(field) == 10:
        return {
            'move': None,
            'score': - 1 * ((9 - np.count_nonzero(field)) + 1)
        }
    elif checkForWin(field) == -10:
        return {
            'move': None,
            'score': 1 * ((9 - np.count_nonzero(field)) + 1)
        }
    elif checkForWin(field) == 1000:
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
                    sim_score = minimax(field, False, alpha, beta)
                    field[i][j] = 0

                    sim_score['move'] = (i, j)
                    best = max(best, sim_score, key=lambda x: x['score'])
                    alpha = max(alpha, best['score'])
                    if beta <= alpha:
                        break
                    
            elif not isMaximizing:
                if field[i][j] == 0:
                    field[i][j] = 1
                    sim_score = minimax(field, True, alpha, beta)
                    field[i][j] = 0

                    sim_score['move'] = (i, j)
                    best = min(best, sim_score, key=lambda x: x['score'])
                    beta = min(beta, best['score'])
                    if beta <= alpha:
                        break
    return best

def bestmove(field):
    if np.count_nonzero(field) != 9:
        if np.count_nonzero(field) == 0:
            move = (0,0)
        else:
            move = minimax(field, True, -math.inf, math.inf)['move']
        if move != None:
            field[move[0]][move[1]] = -2
    return field

app = Flask(__name__)
fieldModel = ttt.FieldModel()
fieldModel.load_state_dict(torch.load('tictactoeField.pth', map_location='cpu'))
fieldModel.eval()
boardModel = ttt.BoardModel()
boardModel.load_state_dict(torch.load('tictactoeBoard.pth', map_location='cpu'))
boardModel.eval()

def tictactoeState(image, player):
    image = image.resize((168, 168), Image.ANTIALIAS)
    image = image.convert('L')
    imageT = to_tensor(image).reshape(1, 1, 168, 168)
    out = boardModel(imageT)
    bboxes = ttt.cellboxes_to_boxes(out)[0]
    
    fieldDict = {
        '0': torch.zeros((1, 28, 28)),
        '1': torch.zeros((1, 28, 28)),
        '2': torch.zeros((1, 28, 28)),
        '3': torch.zeros((1, 28, 28)),
        '4': torch.zeros((1, 28, 28)),
        '5': torch.zeros((1, 28, 28)),
        '6': torch.zeros((1, 28, 28)),
        '7': torch.zeros((1, 28, 28)),
        '8': torch.zeros((1, 28, 28)),
    }

    confidenceDict = {
        '0': 0,
        '1': 0,
        '2': 0,
        '3': 0,
        '4': 0,
        '5': 0,
        '6': 0,
        '7': 0,
        '8': 0,
    }

    for box in bboxes:
        class_idx = box[0]
        confidence = box[1]
        if confidence > confidenceDict[str(int(class_idx))]:
            x = box[2] * 168
            y = box[3] * 168
            w = box[4] * 168
            h = box[5] * 168
            im1 = image.crop(
                (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            )
            im1 = im1.resize((28, 28))
            fieldDict[str(int(class_idx))] = to_tensor(im1)

    fields = torch.stack(list(fieldDict.values()))

    out = fieldModel(fields)
    state = out.argmax(1).numpy().reshape(3, 3) - 1
    state *= player
    state = bestmove(state)
    state *= player

    return state.astype(int).tolist()

@app.route("/state", methods=['POST'])
def getState():
    image = request.files['image']
    image = Image.open(image)
    width, height = image.size
    image = image.crop((
        max(0, (width - height) / 2), 
        max(0, (height - width) / 2), 
        width - max(0, (width - height) / 2),
        height - max(0, (height - width) / 2)
    ))
    game = int(request.form['game'])
    player = int(request.form['player'])
    if game == 1:
        state = tictactoeState(image, player)
    elif game == 2:
        state = connectFourState(image)
    else:
        state = []
    return jsonify({'state': state})

@app.route("/game", methods=['POST'])
def getGame():
    game = 1
    return jsonify({'game': game})

if __name__ == "__main__":
    app.run(host='0.0.0.0')

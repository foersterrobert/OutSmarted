import base64
from flask import Flask, jsonify, request
from PIL import Image
from ConnectFour.detect import connectfourDetect as cfDetect
from ConnectFour.move import connectfourMove as cfMove
from TicTacToe.detect import tictactoeDetect as tttDetect
from TicTacToe.move import tictactoeMove as tttMove
from torchvision.transforms.functional import to_tensor
import torch
import math
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
plt.switch_backend('agg')

app = Flask(__name__)

# tictactoe models
fieldModel = tttDetect.FieldModel()
fieldModel.load_state_dict(torch.load('TicTacToe/detect/tictactoeField.pth', map_location='cpu'))
fieldModel.eval()
boardModel = tttDetect.BoardModel()
boardModel.load_state_dict(torch.load('TicTacToe/detect/tictactoeBoard.pth', map_location='cpu'))
boardModel.eval()

def connectfourState(image, player):
    try:
        state = cfDetect.detectBoard(image)
        state *= player
        state = np.flip(state, 0)
    except:
        state = np.zeros((6, 7))
        image.save('image.png')
    col, _ = cfMove.minimax(state, 5, -math.inf, math.inf, True)
    state *= player
    if col:
        if cfMove.is_valid_location(state, col):
            row = cfMove.get_next_open_row(state, col)
            cfMove.drop_piece(state, row, col, player*-2)
    state = np.flip(state, 0)
    return state.astype(int).tolist()

def tictactoeState(image, player):
    image = image.resize((168, 168), Image.ANTIALIAS)

    fig, ax = plt.subplots(1)
    plt.axis('off')
    ax.imshow(image)

    image = image.convert('L')
    imageT = to_tensor(image).reshape(1, 1, 168, 168)
    out = boardModel(imageT)
    converted_pred = tttDetect.convert_cellboxes(out).reshape(out.shape[0], 36, -1)
    converted_pred[..., 0] = converted_pred[..., 0].long()
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

    for bbox_idx in range(36):
        class_idx, confidence, x, y, w, h = [val.item() for val in converted_pred[0, bbox_idx, :]]
        if confidence > confidenceDict[str(int(class_idx))]:
            x = x * 168
            y = y * 168
            w = w * 168
            h = h * 168
            im1 = image.crop(
                (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            )
            im1 = im1.resize((28, 28))
            fieldDict[str(int(class_idx))] = to_tensor(im1)
            confidenceDict[str(int(class_idx))] = confidence
            rect = Rectangle(
                (x - w / 2, y - h / 2),
                x,
                y,
                linewidth=1,
                edgecolor='r',
                facecolor='none'
            )
            ax.add_patch(rect)

    fields = torch.stack(list(fieldDict.values()))
    out = fieldModel(fields)
    state = out.argmax(1).numpy().reshape(3, 3) - 1

    state *= player
    state = tttMove.bestmove(state)
    state *= player
    fig.savefig('image.png', bbox_inches='tight', pad_inches=0)

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
        state = connectfourState(image, player)
    else:
        state = []
    with open('image.png', 'rb') as f:
        imageJson = base64.b64encode(f.read()).decode('ascii')

    return jsonify({'state': state, 'image': imageJson})

@app.route("/game", methods=['POST'])
def getGame():
    game = 1
    return jsonify({'game': game})

if __name__ == "__main__":
    app.run(host='0.0.0.0')

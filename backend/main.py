from flask import Flask, jsonify, request
from PIL import Image
from ConnectFour.detect.connectfour import connectFourState
from backend.TicTacToe.detect import tictactoeDetect as tttDetect
from backend.TicTacToe.move import tictactoeMove as tttMove
from torchvision.transforms.functional import to_tensor
import torch
from PIL import Image

app = Flask(__name__)

# tictactoe models
fieldModel = tttDetect.FieldModel()
fieldModel.load_state_dict(torch.load('TicTacToe/detect/tictactoeField.pth', map_location='cpu'))
fieldModel.eval()
boardModel = tttDetect.BoardModel()
boardModel.load_state_dict(torch.load('TicTacToe/detect/tictactoeBoard.pth', map_location='cpu'))
boardModel.eval()

def tictactoeState(image, player):
    image = image.resize((168, 168), Image.ANTIALIAS)
    image = image.convert('L')
    imageT = to_tensor(image).reshape(1, 1, 168, 168)
    out = boardModel(imageT)
    bboxes = tttDetect.cellboxes_to_boxes(out)[0]
    
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
    state = tttMove.bestmove(state)
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

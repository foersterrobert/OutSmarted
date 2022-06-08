import base64
from flask import Flask, jsonify, request
from PIL import Image
from Classification import classification as cl
from ConnectFour.detect import connectfourDetect as cfDetect
from ConnectFour.move import connectfourMove as cfMove
from TicTacToe.detect import tictactoeDetect as tttDetect
from TicTacToe.move import tictactoeMove as tttMove
from torchvision.transforms.functional import to_tensor
import torch
from PIL import Image
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
plt.switch_backend('agg')

app = Flask(__name__)

# classification model
classificationModel = cl.Model()
classificationModel.load_state_dict(torch.load('Classification/classificaton.pth', map_location='cpu'))
classificationModel.eval()

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
        state = state.reshape(7*6).tolist()
    except Exception:
        state = [0] * 42
        image.save('image.png')
    if not cfMove.is_terminal(state):
        column = cfMove.mcts(state, player)
        cfMove.drop_piece(state, column, player*-2)
    state = [state[i:i+7] for i in range(0, 42, 7)]
    return state

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

    boxDict = {
        '0': [0, 0, 0, 0, 0],
        '1': [0, 0, 0, 0, 0],
        '2': [0, 0, 0, 0, 0],
        '3': [0, 0, 0, 0, 0],
        '4': [0, 0, 0, 0, 0],
        '5': [0, 0, 0, 0, 0],
        '6': [0, 0, 0, 0, 0],
        '7': [0, 0, 0, 0, 0],
        '8': [0, 0, 0, 0, 0],
    }

    fields = []

    for bbox_idx in range(36):
        class_idx, confidence, x, y, w, h = [val.item() for val in converted_pred[0, bbox_idx, :]]
        if confidence > boxDict[str(int(class_idx))][0]:
            boxDict[str(int(class_idx))] = [confidence, x, y, w, h]

    for i in range(9):
        confidence, x, y, w, h = boxDict[str(i)]
        if confidence > 0:
            x = x * 168
            y = y * 168
            w = w * 168
            h = h * 168
            im1 = image.crop(
                (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            )
            im1 = im1.resize((28, 28))
            im1 = to_tensor(im1)
            fields.append(im1)
            rect = Rectangle(
                (x - w / 2, y - h / 2),
                x,
                y,
                linewidth=1,
                edgecolor='r',
                facecolor='none'
            )
            ax.add_patch(rect)
        else:
            fields.append(torch.zeros((1, 28, 28)))

    fields = torch.stack(fields)
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
    imageT = to_tensor(image).reshape(1, 1, 168, 168)
    out = torch.exp(classificationModel(imageT))
    game = out.argmax(1).item() + 1
    vals = out.squeeze().detach().numpy().tolist()
    vals = [round(val, 4) for val in vals]

    return jsonify({'game': game, 'out': vals})

if __name__ == "__main__":
    app.run(host='0.0.0.0')

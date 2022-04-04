import numpy as np
from flask import Flask, jsonify, request
import cv2
from PIL import Image
import tictactoe as ttt
from connectfour import connectFourState
import math

app = Flask(__name__)

@app.route("/", methods=['POST'])
def index():
    image = request.files['image']
    image = Image.open(image)
    width, height = image.size
    image = image.crop((
        max(0, (width - height) / 2), 
        max(0, (height - width) / 2), 
        width - max(0, (width - height) / 2),
        height - max(0, (height - width) / 2)
    ))
    game = 1 # int(request.form['game'])
    try:
        if game == 1:
            state = tictactoeState(image)
        elif game == 2:
            state = connectFourState(image)
        else:
            state = []
    except Exception:
        state = []
    print(state)
    return jsonify({'state': state, 'game': game})

# MINIMAX ALGORITHM START
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

def minimax(field, isMaximizing):
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

def bestmove(field):
    if np.count_nonzero(field) != 9:
        move = minimax(field, True)['move']
        field[move[0]][move[1]] = -2
    return field

def tictactoeState(image):
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    resized_original_image = cv2.resize(image, (480, 480))
    img = ttt.pre_processing(resized_original_image)
    img = ttt.build_around_to_500(img)
    contours = ttt.find_contours(img, 3)
    contours = ttt.move_contours_back_to_480(contours)
    state = ttt.find_digital_game_array(contours, ttt.recognize_contour_type)
    state = bestmove(state)
    return state.astype(int).tolist()

if __name__ == "__main__":
    app.run(host='0.0.0.0')

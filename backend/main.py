import numpy as np
from flask import Flask, jsonify, request
import cv2
from PIL import Image
import tictactoe as ttt
from connectfour import connectFourState

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
    image.save('image.jpg')
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

def tictactoeState(image):
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    resized_original_image = cv2.resize(image, (480, 480))
    img = ttt.pre_processing(resized_original_image)
    img = ttt.build_around_to_500(img)
    contours = ttt.find_contours(img, 3)
    contours = ttt.move_contours_back_to_480(contours)
    state = ttt.find_digital_game_array(contours, ttt.recognize_contour_type)
    return state

app.run(host='0.0.0.0')
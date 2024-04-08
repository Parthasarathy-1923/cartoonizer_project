from flask import Flask, render_template, request
import cv2
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

app = Flask(__name__)

class Cartoonizer:
    def __init__(self):
        pass

    def render(self, img_rgb):
        img_rgb = cv2.imdecode(np.fromstring(img_rgb.read(), np.uint8), cv2.IMREAD_COLOR)

        numDownSamples = 2
        numBilateralFilters = 50
        img_color = img_rgb
        for _ in range(numDownSamples):
            img_color = cv2.pyrDown(img_color)
        for _ in range(numBilateralFilters):
            img_color = cv2.bilateralFilter(img_color, 8, 8, 6)
        for _ in range(numDownSamples):
            img_color = cv2.pyrUp(img_color)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        img_blur = cv2.medianBlur(img_gray, 3)
        img_edge = cv2.adaptiveThreshold(img_blur, 255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY, 5, 2)
        (x,y,z) = img_color.shape
        img_edge = cv2.resize(img_edge,(y,x))
        img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)

        res = cv2.bitwise_and(img_color, img_edge)

        # Convert result to base64 string to display in HTML
        _, buffer = cv2.imencode('.jpg', res)
        res_base64 = base64.b64encode(buffer)
        res_str = res_base64.decode('utf-8')
        return res_str

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file:
        cartoonizer = Cartoonizer()
        result = cartoonizer.render(file)
        return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)

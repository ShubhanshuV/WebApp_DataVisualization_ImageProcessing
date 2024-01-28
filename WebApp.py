from flask import Flask, render_template, request,send_file,url_for
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os
import cv2
import numpy as np
import tempfile

app = Flask(__name__)

def generate_charts(df):
  
    plt.switch_backend('agg')

    grouped = df.groupby(df.columns[0]).sum()

   
    categories = grouped.index
    amounts = grouped.values.flatten()

  
    pie_chart = plt.figure(figsize=(8, 6))
    labels = [f"{category}: {amount:.2f}" for category, amount in zip(categories, amounts)]
    plt.pie(amounts, labels=labels, autopct='%1.1f%%')
    plt.title('Pie Chart')
    pie_img = BytesIO()
    plt.savefig(pie_img, format='png')
    pie_img.seek(0)
    pie_url = base64.b64encode(pie_img.getvalue()).decode('utf-8')

    
    bar_chart = plt.figure(figsize=(10, 6))
    plt.bar(categories, amounts)
    plt.xlabel(df.columns[0])
    plt.ylabel('Total')
    plt.title('Bar Chart')
    bar_img = BytesIO()
    plt.savefig(bar_img, format='png')
    bar_img.seek(0)
    bar_url = base64.b64encode(bar_img.getvalue()).decode('utf-8')

    return pie_url, bar_url


@app.route('/')
def index():
    return render_template('index.html')

def convert_to_grayscale(file):
    
    _, temp_filename = tempfile.mkstemp(suffix='.png')
    file.save(temp_filename)
    image = cv2.imread(temp_filename)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray_bytes = cv2.imencode('.png', gray_image)[1].tobytes()

    gray_io = BytesIO(gray_bytes)

    # Remove the temporary file
    os.remove(temp_filename)

    return gray_io
@app.route('/upload', methods=['POST'])
def upload():
    global gray_io
    #gloabl file
    if 'file' not in request.files:
        return render_template('index.html', message='No file part')

    file = request.files['file']

    if file.filename == '':
        return render_template('index.html', message='No selected file.Please select csv or image file!')

    if file:
       
        _, file_ext = os.path.splitext(file.filename)

        if file_ext.lower() == '.csv':
            df = pd.read_csv(file)
            pie_url, bar_url = generate_charts(df)
            return render_template('result.html', pie_url=pie_url, bar_url=bar_url)
        elif file_ext.lower() in ('.png', '.jpg', '.jpeg'):
            gray_io = convert_to_grayscale(file)
            encoded_image = base64.b64encode(gray_io.getvalue()).decode('utf-8')
            return render_template('display.html', image_data=encoded_image)
        else:
            return render_template('index.html', message='Unsupported file type.Please select csv or image(jpg/png or jpeg) file!')

    return render_template('index.html', message='Error occurred')

@app.route('/display_image')
def display_image():
   
    return send_file(gray_io, mimetype='image/png')

@app.route('/download_image')
def download_image():
    
    return send_file(gray_io, mimetype='image/png', as_attachment=True, download_name='grayscale_image.png')



if __name__ == '__main__':
    app.run(debug=True)





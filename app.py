from flask import Flask
from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import bcrypt
from PIL import Image
import numpy as np
import joblib
import tensorflow as tf
from keras.models import load_model
# from model import preprocess_input

app = Flask(__name__)
cors = CORS(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'your_database_name'

mysql = MySQL(app)

# ========================= loading my model ============================
model_txt = joblib.load('model_text.sav')

# ======================== end model load ===============================


# ========================= define preprocessing function ===============
# Define a preprocessing function for the endpoint
# Define a preprocessing function for the endpoint
def preprocess_input(img):
    img = img.astype('float32')
    img /= 255.0
    return img

def preprocess_image(img):
    img = img.resize((224, 224))
    img_array = np.array(img)
    img_array = preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


@app.route('/users/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password'].encode('utf-8')

    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    # Store the hashed password in the database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'User registered successfully.'})

@app.route('/users/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password'].encode('utf-8')

    # Retrieve the hashed password from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cur.fetchone()
    cur.close()

    if result is None:
        return jsonify({'message': 'Invalid username or password.'})

    hashed_password = result[0]

    # Check if the password matches the hashed password using bcrypt
    if bcrypt.checkpw(password, hashed_password.encode('utf-8')):
        return jsonify({'message': 'Login successful.'})
    else:
        return jsonify({'message': 'Invalid username or password.'})
    

# Define an endpoint for testing the model
@app.route('/predict', methods=['POST'])
def predict():
    image_file = request.files['image']
    image = Image.open(image_file)
    x = preprocess_image(image)
    predictions = model.predict(x)
    if predictions[0] < 0.5:
        prediction_text = 'Real'
    else:
        prediction_text = 'Fake'
    return jsonify({'prediction': prediction_text})


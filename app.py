import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template, redirect, flash, url_for, session
from sklearn.preprocessing import MinMaxScaler
from werkzeug.utils import secure_filename
import pickle
import sqlite3
import os

app = Flask(__name__)  # Initialize the flask App
app.secret_key = 'your_secret_key'  # Needed for session and flash messages

# Load your ML model
fraud = pickle.load(open('fraud.pkl', 'rb'))

# Database file path
DATABASE = 'usersa.db'

# Initialize database if it doesn't exist
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/')
@app.route('/first')
def first():
    return render_template('first.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form['uname']
        password = request.form['pwd']

        # Validate credentials
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            # Set session variables
            session['logged_in'] = True
            session['username'] = username
            return jsonify({'success': True, 'redirect_url': url_for('upload')})
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']

        try:
            # Add user to database
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            flash('Registration Successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/upload')
def upload():
    if not session.get('logged_in'):
        flash('You must log in to access this page.', 'danger')
        return redirect(url_for('login'))
    return render_template('upload.html')

# @app.route('/preview', methods=["POST"])
# def preview():
DEFAULT_FILE_PATH = "../upload.csv"

@app.route('/preview', methods=["POST"])
def preview():
    if 'datasetfile' in request.files and request.files['datasetfile'].filename != '':
        # Case 1: User uploaded a file via <input type="file">
        dataset = request.files['datasetfile']
        print("User uploaded file: {}".format(dataset.filename))
    else:
        # Case 2: User clicked "Use Default File"
        dataset = DEFAULT_FILE_PATH
        print("Using default file: {}".format(DEFAULT_FILE_PATH))

    # Read the dataset (either uploaded or default)
    df = pd.read_csv(dataset, encoding='unicode_escape')
    df.set_index('Id', inplace=True)

    return render_template("preview.html", df_view=df)

    # if request.method == 'POST':
    #     dataset = request.files['datasetfile']
    #
    #     # Ensure file exists
    #     if dataset:
    #         df = pd.read_csv(dataset, encoding='unicode_escape')
    #         df.set_index('Id', inplace=True)
    #         return render_template("preview.html", df_view=df)
    #     else:
    #         flash('No file uploaded or selected.', 'danger')
    #         return redirect(url_for('upload'))
    # if request.method == 'POST':
    #     dataset = request.files['datasetfile']
    #     print("check{}".format(dataset))
    #
    #
    #     df = pd.read_csv(dataset, encoding='unicode_escape')
    #     df.set_index('Id', inplace=True)
    #     return render_template("preview.html", df_view=df)

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    return render_template('prediction.html')

@app.route('/predict', methods=['POST'])
def predict():
    int_feature = [x for x in request.form.values()]
    final_features = [np.array(int_feature)]
    result = fraud.predict(final_features)
    result = "Transaction Fraudulent" if result == 1 else 'Benign'
    return render_template('prediction.html', prediction_text=result)

@app.route('/performance')
def performance():
    return render_template('performance.html')

@app.route('/chart')
def chart():
    return render_template('chart.html')

@app.route('/logout')
def logout():
    session.clear()  # Clear session data
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == "__main__":
    init_db()  # Ensure the database is initialized
    app.run(debug=True)

# import numpy as np
# import pandas as pd
# from flask import Flask, request, jsonify, render_template, redirect, flash, url_for
# from sklearn.preprocessing import MinMaxScaler
# from werkzeug.utils import secure_filename
# import pickle
# import sqlite3
# import os
#
# app = Flask(__name__)  # Initialize the flask App
# app.secret_key = 'your_secret_key'  # Needed for flash messages
#
# # Load your ML model
# fraud = pickle.load(open('fraud.pkl', 'rb'))
#
# # Database file path
# DATABASE = 'usersa.db'
#
# # Initialize database if it doesn't exist
# def init_db():
#     if not os.path.exists(DATABASE):
#         conn = sqlite3.connect(DATABASE)
#         c = conn.cursor()
#         c.execute('''
#             CREATE TABLE users (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 username TEXT UNIQUE NOT NULL,
#                 password TEXT NOT NULL
#             )
#         ''')
#         conn.commit()
#         conn.close()
#
# @app.route('/')
# @app.route('/first')
# def first():
#     return render_template('first.html')
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         # Get form data
#         username = request.form['uname']
#         password = request.form['pwd']
#
#         # Validate credentials
#         conn = sqlite3.connect(DATABASE)
#         c = conn.cursor()
#         c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
#         user = c.fetchone()
#         conn.close()
#
#         if user:
#             print("pass")
#             return jsonify({'success': True, 'redirect_url': url_for('upload')})
#         else:
#             print("fail")
#             return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
#
#     return render_template('login.html')
#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         # Get form data
#         username = request.form['username']
#         password = request.form['password']
#
#         try:
#             # Add user to database
#             conn = sqlite3.connect(DATABASE)
#             c = conn.cursor()
#             c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
#             conn.commit()
#             conn.close()
#             flash('Registration Successful! You can now log in.', 'success')
#             return redirect(url_for('login'))
#         except sqlite3.IntegrityError:
#             flash('Username already exists. Please choose a different one.', 'danger')
#             return redirect(url_for('register'))
#
#     return render_template('register.html')
#
# @app.route('/upload')
# def upload():
#     return render_template('upload.html')
#
# @app.route('/preview', methods=["POST"])
# def preview():
#     if request.method == 'POST':
#         dataset = request.files['datasetfile']
#         df = pd.read_csv(dataset, encoding='unicode_escape')
#         df.set_index('Id', inplace=True)
#         return render_template("preview.html", df_view=df)
#
# @app.route('/prediction', methods=['GET', 'POST'])
# def prediction():
#     return render_template('prediction.html')
#
# @app.route('/predict', methods=['POST'])
# def predict():
#     int_feature = [x for x in request.form.values()]
#     final_features = [np.array(int_feature)]
#     result = fraud.predict(final_features)
#     result = "Transaction Fraudulent" if result == 1 else 'Benign'
#     return render_template('prediction.html', prediction_text=result)
#
# @app.route('/performance')
# def performance():
#     return render_template('performance.html')
#
# @app.route('/chart')
# def chart():
#     return render_template('chart.html')
#
# if __name__ == "__main__":
#     init_db()  # Ensure the database is initialized
#     app.run(debug=True)

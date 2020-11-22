from datetime import datetime
from time import strftime
import os

from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, send, emit
from pymongo.errors import DuplicateKeyError

from db import save_user, get_user, get_box, save_box

heroku_env = os.getenv("HEROKU_ENV_SELECTED")

server = 'https://keepit-remote.herokuapp.com/' if heroku_env else 'http://127.0.0.1:5000/'



# Setup app with web socket and Login Handler
app = Flask(__name__)
app.secret_key = "KeepItSecret"
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# Splash screen
@app.route('/')
def home():
    return render_template("index.html", server=server)

# Login screen
@app.route('/login', methods=['GET','POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')

        user = get_user(username)

        if user and user.check_password(password_input):
            succes_message = " not " if user.check_password(password_input) else ""
            app.logger.info(
                f"{username} tried with {password_input} and did{succes_message}succeed.")
            login_user(user)
            return redirect(url_for('box_overview'))
        else:
            if user: 
                app.logger.info("Failed password")
            else:
                app.logger.info("User not registered")
            message = "Username or Password incorrect"

    return render_template('login.html', message = message, server=server)

# Logout
@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Login screen
@app.route('/signup', methods=['GET','POST'])
def signup():
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')
        email_input = request.form.get('email')
        box_name_input = request.form.get('box_name')

        user = save_user(username,email_input,password_input,box_name_input)
    
        if user:
            save_box(box_name_input)
            app.logger.info(
                f"{username} added with box {box_name_input} linked to its account.")
            login_user(user)
            return redirect(url_for('box_overview'))
        else:
            if not get_box(box_name_input): 
                app.logger.info(f"{username} already used")
                message = "Username already exist, please try with another one."
            else:
                app.logger.info("Box already in use")
                message = "Box name already registered."

    return render_template('signup.html', message = message, server=server)

# User screen
@app.route('/box')
@login_required
def box_overview():
    app.logger.info(f"/box on {server}")
    username = current_user.username
    box_name = current_user.box_name

    # Date and time string
    date_time = strftime('%H:%M')

    if username and box_name:
        return render_template("box.html", username=username, box_name=box_name, events_registered=[], server=server)
    else:
        app.logger.info(f"{username} was redirected to home after trying {box_name}.")
        return redirect(url_for("home"))

# Box register event
@app.route('/register_event', methods=['POST'])
@login_required
def register_event():
    data = request.get_json(force=True)

    app.logger.info(data)
    app.logger.info(f"/register_event on {server}")

    if data.get('action') is None or data.get('date') is None:
        return jsonify({'message': 'Bad request'}), 400

    emit('receive_event', data=data, broadcast=True)
    return "Event sent"

@socketio.on('join_room')
def handle_join_event(data):
    app.logger.info(f"{data['username']} has joined box {data['box_name']}")

@login_manager.user_loader
def load_user(username):
    return get_user(username)

if __name__ == '__main__':
    import argparse
    socketio.run(app, debug=True)

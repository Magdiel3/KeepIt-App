from datetime import datetime
from time import strftime
import os

from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, send, emit
from flask_qrcode import QRcode
from pymongo.errors import DuplicateKeyError

from db import save_user, get_user, get_box, save_box, is_box_owner

# Setup app with web socket and Login Handler
app = Flask(__name__)
app.secret_key = "KeepItSecret"
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)
qrcode = QRcode(app)

# Splash screen
@app.route('/')
def home():
    return render_template("index.html")

# Login screen
@app.route('/login', methods=['GET','POST'])
def login():
    message = ''

    if current_user.is_authenticated:
        return redirect(f"box/{current_user.box_name}/")

    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')

        user = get_user(username)

        if user and user.check_password(password_input):
            succes_message = " not " if user.check_password(password_input) else ""
            app.logger.info(
                f"{username} tried with {password_input} and did{succes_message}succeed.")
            login_user(user)
            return redirect(f"/box/{user.box_name}/")
        else:
            if user: 
                app.logger.info("Failed password")
            else:
                app.logger.info("User not registered")
            message = "Username or Password incorrect"

    return render_template('login.html', message = message)

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
            return redirect(f"box/{user.box_name}/")
        else:
            if not get_box(box_name_input): 
                app.logger.info(f"{username} already used")
                message = "Username already exist, please try with another one."
            else:
                app.logger.info("Box already in use")
                message = "Box name already registered."

    return render_template('signup.html', message = message)

# User screen
@app.route('/box/<box_name_url>/')
@login_required
def box_overview(box_name_url):
    app.logger.info(f"/box/{box_name_url}")
    username = current_user.username
    box_name = current_user.box_name

    # Date and time string
    date_time = strftime('%H:%M')

    if username and is_box_owner(username,box_name_url):
        return render_template("box.html", username=username, box_name=box_name, events_registered=[], 
                        )
    else:
        app.logger.info(f"{username} was redirected to home after trying {box_name}.")
        abort(403, description="Acces denied")
        return jsonify({
                'message': 'Acces Denied',
                'box_owned': box_name,
                'box_tried': box_name_url
            })


# User QR key
@app.route('/box/<box_name_url>/access_key/')
@login_required
def show_qr_key(box_name_url):
    app.logger.info(f"{current_user.username} retrieving key for {box_name_url}")
    user_box = current_user.box_name

    if box_name_url and is_box_owner(currentuser.username,box_name_url):
        app.logger.info(f"{current_user.username} has secceufully retrieved {current_user.box_name} key")
        return render_template("qr_code.html", username=current_user.username,
                                box_name=current_user.box_name, box_key=f"bosname:{current_user.box_name}")
    else:
        app.logger.info(f"{current_user.username} is not owner of {box_name_url}")
        abort(403, description="Acces denied")
        return jsonify({
                'message': 'Acces Denied',
                'box_owned': box_name,
                'box_tried': box_name_url
            })


# Box register event
@app.route('/register_event/', methods=['POST'])
@login_required
def register_event():
    data = request.get_json(force=True)

    app.logger.info(data)
    box_name = data.get('box_name','')

    if data.get('action') is None or data.get('date') is None or box_name is None:
        return jsonify({'message': 'Bad request'}), 400

    if get_box(box_name):
        socketio.emit(f'receive_event/{box_name}', data=data, box_name=data.get('box_name'))
        return f"Event sent to {box_name}"
    else:
        app.logger.info(f"Box {box_name} was not found")
        return "Box not found"

@socketio.on('join_room')
def handle_join_event(data):
    app.logger.info(f"{data['username']} has joined box {data['box_name']}")

@login_manager.user_loader
def load_user(username):
    return get_user(username)

if __name__ == '__main__':
    import argparse
    socketio.run(app, debug=True)

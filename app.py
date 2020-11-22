from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, join_room, leave_room
from pymongo.errors import DuplicateKeyError

from db import save_user, get_user

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
    return render_template("index.html")

# Login screen
@app.route('/login', methods=['GET','POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')

        user = get_user(username)

        if user and user.check_password(password_input):
            succes_message = user.check_password(password_input)
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

    return render_template('login.html', message = message)

# Logout
@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# User screen
@app.route('/box')
@login_required
def box_overview():
    username = current_user.username
    box_name = current_user.box_name

    if username and box_name:
        return render_template("box.html",username=username, box_name=box_name)
    else:
        return redirect(url_for("home"))

@socketio.on('join_room')
def handle_join_event(data):
    app.logger.info(f"{data['username']} has joined box {data['box_name']}")

@login_manager.user_loader
def load_user(username):
    return get_user(username)

if __name__ == '__main__':
    app.run(debug=True)

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
            login_user(user)
            return redirect(url_for('home'))
        else:
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
def overview():
    username = request.args.get("username")
    password = request.args.get("box_id")
    
    if username and password:
        return render_template("home.thml",username=username, password=password)
    else:
        return redirect(url_for("/"))

@login_manager.user_loader
def load_user(username):
    return get_user(username)

if __name__ == '__main__':
    app.run(debug=True)

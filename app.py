from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, join_room, leave_room
from pymongo.errors import DuplicateKeyError


# Setup app with web socket and Login Handler
app = Flask(__name__)
# app.secret_key = "keepit"
# socketio = SocketIO(app)
# login_manager = LoginManager()
# login_manager.login_view = 'login'
# login_manager.init_app(app)


# Splash screen
@app.route('/')
def home():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=False)

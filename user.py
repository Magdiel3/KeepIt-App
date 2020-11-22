from werkzeug.security import check_password_hash


class User:

    def __init__(self, username, email, password, box_name):
        self.username = username
        self.email = email
        self.password = password
        self.box_name = box_name

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username

    def check_password(self, password_input):
        return check_password_hash(self.password, password_input)

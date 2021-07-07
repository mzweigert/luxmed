from flask_login import UserMixin


class UserClass(UserMixin):
    def __init__(self, _email, _id, _active=True):
        self.email = _email
        self.id = _id
        self.active = _active

    def is_active(self):
        return self.active


def form_dictionary(dictionary: dict):
    return UserClass(dictionary['email'], dictionary['id'])

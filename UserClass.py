from flask_login import UserMixin


class UserClass(UserMixin):
    def __init__(self, name, _id, active=True):
        self.name = name
        self.id = _id
        self.active = active

    def is_active(self):
        return self.active

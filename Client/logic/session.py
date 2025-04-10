# Client/logic/session.py

class Session:
    def __init__(self):
        self.user = None

    def set_user(self, user):
        self.user = user

    def get_user(self):
        return self.user

# Global session object
session = Session()

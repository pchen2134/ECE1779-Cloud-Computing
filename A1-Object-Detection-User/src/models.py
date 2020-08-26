from flask_login import UserMixin
from . import db
from src import login_manager

'''
    User Model
'''
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    def __repr__(self):
        return '<User {}, {}>'.format(self.username, self.id)


'''
    Photo Model
'''
class Photo(UserMixin, db.Model):
    __tablename__ = 'photos'
    userid = db.Column(db.Integer)
    picname = db.Column(db.String(120), primary_key=True)

    def __init__(self, userid, picname):
        self.userid = userid
        self.picname = picname

    def __repr__(self):
        return '<Photo {}, {}>'.format(self.userid, self.picname)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

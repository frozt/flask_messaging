from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy.orm import relationship


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trioptima.db'
db = SQLAlchemy(app)
db.init_app(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)

    def __init__(self, username):
        self.username = username

    def __str__(self):
        return self.username


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(20))
    receiver = db.Column(db.String(20))
    message = db.Column(db.Text)
    msg_timestamp = db.Column(db.DateTime)
    fetched = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean)

    def __init__(self, sender, receiver, message):
        self.sender = sender
        self.receiver = receiver
        self.message = message
        self.msg_timestamp = datetime.datetime.now()
        self.fetched = False
        self.deleted = False

    def toJson(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'time': self.msg_timestamp,
            'message': self.message
        }





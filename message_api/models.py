from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import json

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

    def __init__(self, sender, receiver, message):
        self.sender = sender
        self.receiver = receiver
        self.message = message
        self.msg_timestamp = datetime.datetime.now()
        self.fetched = False

    def __repr__(self):
        return json.dumps(self.__dict__)





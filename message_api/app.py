from flask import request, jsonify
from os import abort
from models import User, Message, db, app


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/init')
def init():
    db.create_all()

    user_a = User('a')
    user_b = User('b')
    db.session.add(user_a)
    db.session.add(user_b)
    db.session.commit()
    return 'Success'


@app.route('/get_messages', methods=['GET'])
def get_messages():
    pass


@app.route('/get', methods=['GET'])
def get_single_message():
    pass


@app.route('/fetch/<string:username>', methods=['GET'])
def fetch_new_messages(username):
    new_msgs = Message.query.filter_by(receiver=username, fetched=False).all()
    for msg in new_msgs:
        msg.fetched = True

    db.session.commit()
    return jsonify(dict(new_msgs))


@app.route('/send', methods=['POST'])
def send_message():
    if not request.json:
        abort(400)

    try:
        msg = Message(request.json['sender'], request.json['receiver'], request.json['message'])
        db.session.add(msg)
        db.session.commit()
        return 'Successfully inserted'
    except KeyError:
        abort(400)


@app.route('/delete', methods=['POST'])
def delete_message():
    pass


if __name__ == '__main__':
    app.run(debug=True)

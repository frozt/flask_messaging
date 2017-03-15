from flask import request, jsonify
from flask.views import MethodView
from os import abort
from models import User, Message, db, app


class JsonPostRequest(MethodView):
    def post(self):
        # check if request is in json format
        if not request.json:
            abort(400)

        # if one of the required keys is missing abort request
        try:
            return self.process_post()
        except KeyError:
            abort(400)

    def process_post(self):
        raise NotImplementedError()


class SendMessage(JsonPostRequest):
    def process_post(self):
        msg = Message(request.json['sender'], request.json['receiver'], request.json['message'])
        db.session.add(msg)
        db.session.commit()
        return 'Successfully inserted'

app.add_url_rule('/send', view_func=SendMessage.as_view('send'))

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



@app.route('/get_messages', methods=['POST'])
def get_messages():
    pass


@app.route('/get/<int:id>', methods=['GET'])
def get_single_message(id):
    msg = Message.query.filter_by(id=id, deleted=False).first()
    return jsonify(msg.toJson())


@app.route('/fetch/<string:username>', methods=['GET'])
def fetch_new_messages(username):
    new_msgs = Message.query.filter_by(receiver=username, fetched=False).all()
    msgs_json = list()
    for msg in new_msgs:
        msg.fetched = True
        msgs_json.append(msg.toJson())
    db.session.commit()

    return jsonify(msgs_json)



@app.route('/delete', methods=['POST'])
def delete_message():
    pass


if __name__ == '__main__':
    app.run(debug=True)

from flask import request, jsonify
from flask.views import MethodView
from models import User, Message, db, app


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super(InvalidUsage, self).__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


class JsonPostRequest(MethodView):
    """
    Common class for post requests require json data
    """
    def post(self):
        # check if request is in json format
        if not request.json:
            raise InvalidUsage('Json format needed')

        # if one of the required keys is missing abort request
        try:
            return self.process_post()
        except KeyError, key:
            raise InvalidUsage('{} key is missing from json'.format(key))

    def process_post(self):
        raise NotImplementedError()


class MessagesApi(JsonPostRequest):
    """
    Message model related view with get, post, delete functionalities
    """
    def process_post(self):
        """
        Retrieves multiple messages with timestamp order with start and end indexes
        """
        check_user(request.json['username'])
        start = request.json['start'] if 'start' in request.json else None
        end = request.json['end'] if 'end' in request.json else None

        msgs = db.session.query(Message).filter_by(receiver=request.json['username'], deleted=False)\
            .order_by(Message.msg_timestamp)
        if start and not end:
            msgs = msgs.offset(start)

        if end and not start:
            msgs = msgs.limit(end)

        if start and end:
            msgs = msgs.slice(start, end)

        return jsonify([msg.toJson() for msg in msgs])

    def get(self, msg_id):
        """
        Gets single message
        """
        msg = db.session.query(Message).filter_by(id=msg_id, deleted=False).first()
        return jsonify(msg.toJson())

    def delete(self, msg_id):
        """
        Delete single message
        """
        db.session.query(Message).filter_by(id=msg_id).update({Message.deleted: True})
        commit_changes()
        return '{} deleted'.format(msg_id)

messages_view = MessagesApi.as_view('messages_api')
app.add_url_rule('/messages', view_func=messages_view, methods=['POST'])
app.add_url_rule('/messages/<int:msg_id>', view_func=messages_view, methods=['GET', 'DELETE'])


class SendMessage(JsonPostRequest):
    """
    View that handles message send functionality
    """
    def process_post(self):
        check_user(request.json['sender'])
        check_user(request.json['receiver'])

        msg = Message(request.json['sender'], request.json['receiver'], request.json['message'])
        db.session.add(msg)
        commit_changes()
        return 'Successfully inserted'

app.add_url_rule('/send', view_func=SendMessage.as_view('send'))


class DeleteMessages(JsonPostRequest):
    """
    View to handle multiple/single message delete request
    """
    def process_post(self):
        msg_id_list = request.json['messages']

        if any(not isinstance(msg_id, int) for msg_id in msg_id_list):
            raise InvalidUsage('Message id list contains non-int value')

        db.session.query(Message).filter(Message.id.in_(msg_id_list)).update({Message.deleted: True},
                                                                             synchronize_session='fetch')
        commit_changes()
        return '{} deleted'.format(', '.join([str(msg_id) for msg_id in msg_id_list]))


delete_view = DeleteMessages.as_view('delete')
app.add_url_rule('/delete', view_func=delete_view, methods=['POST'])


@app.route('/fetch/<string:username>', methods=['GET'])
def fetch_new_messages(username):
    """
    User specific fetch function to get un-fetched messages
    """
    check_user(username)
    new_msgs = db.session.query(Message).filter_by(receiver=username, fetched=False, deleted=False).all()
    msgs_json = list()
    for msg in new_msgs:
        msg.fetched = True
        msgs_json.append(msg.toJson())
    commit_changes()

    return jsonify(msgs_json)


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/init')
def init():
    """
    Database initialization function
    """
    db.create_all()

    user_a = User('a')
    user_b = User('b')
    db.session.add(user_a)
    db.session.add(user_b)
    commit_changes()
    return 'Success'


def commit_changes():
    """
    Commit changes to database while handling failures
    """
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        db.session.flush()
        raise InvalidUsage(e.message, 500)


def check_user(username):
    """
    Checks if the user exists with the given username
    """
    user = db.session.query(User).filter_by(username=username).first()
    if not user:
        raise InvalidUsage("User {} doesn't exist".format(username))


if __name__ == '__main__':
    app.run(debug=True)

from FlaskWebProject import app
from flask import jsonify


class SecError(Exception):
    status_code = 400

    def to_dict(self):
        rv = {'message': self.message}
        return rv


class IncorrectLoginError(SecError):
    def __init__(self, username):
        SecError.__init__(self)
        self.message = 'Either the username or the password was incorrect for {0}'.format(username)


class InvalidTokenError(SecError):
    def __init__(self):
        SecError.__init__(self)
        self.status_code = 401
        self.message = 'Token is invalid'


class NoTokenError(SecError):
    def __init__(self):
        SecError.__init__(self)
        self.status_code = 401
        self.message = 'No token received for action which requires one'


class NoCollectionPermissionError(SecError):
    def __init__(self, user_type, action, collection):
        SecError.__init__(self)
        self.message = ('Users of type {0} cannot {1} in collection {2}'.format(user_type, action, collection))


class NoDocumentPermissionError(SecError):
    def __init__(self, action, document, collection):
        SecError.__init__(self)
        self.message = 'Client does not have permission to {0} document {1} in collection {2}'.format(action, document,
                                                                                                      collection)


class UnknownUserTypeError(SecError):
    def __init__(self, collection_id, user_type):
        SecError.__init__(self)
        self.status_code = 500
        self.message = 'User type {0} is unknown while accessing collection {1}'.format(user_type, collection_id)


@app.errorhandler(IncorrectLoginError)
@app.errorhandler(InvalidTokenError)
@app.errorhandler(NoTokenError)
@app.errorhandler(NoCollectionPermissionError)
@app.errorhandler(NoDocumentPermissionError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

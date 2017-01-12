from flask import jsonify
from FlaskWebProject import app


class DataError(Exception):
    status_code = 400

    def to_dict(self):
        rv = {'message': self.message}
        return rv


class IllegalAttrError(DataError):
    def __init__(self, id_, collection_id, illegal_attrs):
        DataError.__init__(self)
        self.message = 'The object "{0}" for collection "{1}" had illegal attributes:{2}'.format(id_, collection_id,
                                                                                                 illegal_attrs)


class MissingAttrError(DataError):
    def __init__(self, id_, collection_id, missing_attrs):
        DataError.__init__(self)
        self.message = 'The object "{0}" for collection "{1}" had missing attributes:{2}'.format(id_, collection_id,
                                                                                                 missing_attrs)


class MissingDocsError(DataError):
    def __init__(self, collection_id, missing_doc_ids):
        DataError.__init__(self)
        self.message = 'Documents from collection "{0}" were missing: {1}'.format(collection_id, missing_doc_ids)


class MissingCollectionError(DataError):
    def __init__(self, collection_id):
        DataError.__init__(self)
        self.message = 'The collection "{0}" does not exist'.format(collection_id)


class MissingFunctionError(DataError):
    def __init__(self, user_type, action, collection_id):
        DataError.__init__(self)
        self.message = 'Could not find API function matching user_type:{0}, action:{1}, collection_id:{2}'.format(
            user_type, action, collection_id)


class NonUniqueAttrError(DataError):
    def __init__(self, collection, attr_key, attr_val):
        DataError.__init__(self)
        self.message = 'A doc in collection:{0} with {1}:{2} already exists'.format(collection, attr_key, attr_val)


@app.errorhandler(IllegalAttrError)
@app.errorhandler(MissingAttrError)
@app.errorhandler(MissingDocsError)
@app.errorhandler(MissingCollectionError)
@app.errorhandler(MissingFunctionError)
@app.errorhandler(NonUniqueAttrError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

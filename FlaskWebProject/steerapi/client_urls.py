from flask import request
from FlaskWebProject import app
from FlaskWebProject.steershared.shared_consts import DECODED_TOKEN, USER_TYPE
from data_errors import MissingFunctionError
import io_transformers
import crud_safety
import sec
import pending


@app.route('/')
def home():
    return 'Spot Markets: High Street Client API'


def get_func(module, user_type, action, collection_id):
    """Gets a function from a module based on the user_type, action and collection_id"""
    try:
        return getattr(module, '{0}_{1}_{2}'.format(user_type, action, collection_id))
    except AttributeError:
        pass
    try:
        return getattr(module, '{0}_{1}'.format(user_type, action))
    except AttributeError:
        pass
    try:
        return getattr(module, '{0}_{1}'.format(action, collection_id))
    except AttributeError:
        pass
    try:
        return getattr(module, action)
    except AttributeError:
        raise MissingFunctionError(user_type, action, collection_id)


@app.route('/<collection_id>/<action>', methods=['GET', 'POST'])
@app.route('/<collection_id>/<action>', methods=['GET', 'POST'])
@sec.check_token
def crud_action(headers, collection_id, action):
    print 'HEADERS'
    print str(request.headers)
    user_type = headers[DECODED_TOKEN][USER_TYPE]
    in_data = io_transformers.transform_input(request.data, request.headers, True)
    print '{0} performs {1} on collection {2}'.format(user_type, action, collection_id)
    func = get_func(crud_safety, user_type, action, collection_id)
    out_data = func(collection_id, headers, in_data)
    return io_transformers.transform_output(out_data, request.headers)


@app.route('/sec/<user_type>/<action>', methods=['POST'])
@app.route('/sec/<user_type>/<action>', methods=['POST'])
def user_sec_action(user_type, action):
    print 'HEADERS'
    print str(request.headers)
    in_data = io_transformers.transform_input(request.data, request.headers, False)
    print '{0} called sec action {1}'.format(user_type, action)
    func = get_func(sec, user_type, action, None)
    out_data = func(in_data, request.headers)
    return io_transformers.transform_output(out_data, request.headers)


@app.route('/pending/retailers/read', methods=['POST'])
# @sec.check_token
# def testing(action, headers):
def testing():
    print 'test1'
    print str(request.headers)
    # user_type = headers[DECODED_TOKEN][USER_TYPE]
    # in_data = io_transformers.transform_input(request.data, request.headers, False)
    print '{0} trying to {1}'.format('reda', 'read')
    # func = get_func(pending, user_type, action, 'pending_retailers')
    # TODO: Check if the pending retailer is already there
    # TODO: Check with mike for delete functionality
    # out_data = func('pending_retailers', request.headers, in_data)
    # for testing
    out_data = pending.town_read_pending_retailers('pending_retailers', request.headers, 'a')
    return io_transformers.transform_output(out_data, request.headers)


@app.route('/pending/<user_type>/<action>', methods=['POST'])
def testing1(action,user_type):
    print 'test1'
    print str(request.headers)
    in_data = io_transformers.transform_input(request.data, request.headers, False)
    print '{0} trying to {1}'.format(user_type, action)
    func = get_func(pending, user_type, action, 'pending_retailers')
    # TODO: Check if the pending retailer is already there
    # TODO: Check with mike for delete functionality
    # out_data = pending.create('pending_retailers', request.headers, in_data)
    # out_data = pending.read('pending_retailers', request.headers, in_data)
    out_data = func('pending_retailers', request.headers, in_data)
    return io_transformers.transform_output(out_data, request.headers)

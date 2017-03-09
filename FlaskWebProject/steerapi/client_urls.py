from flask import request
from FlaskWebProject import app
from FlaskWebProject.steershared.shared_consts import DECODED_TOKEN, USER_TYPE
from data_errors import MissingFunctionError
import io_transformers
import crud_safety
import sec
import pending
# modified by C.Pigiotis

# root of API
@app.route('/')
def home():
    return 'Spot Markets: High Street Client API'


# root for api but versioned
@app.route('/<version>')
def home_versioned(version):
    version_for_module = get_version(version)
    print version_for_module

    return 'Spot Markets: High Street Client API' + ' version: ' + version_for_module


# dispatch function for every other call in the API
def get_func(version, module, user_type, action, collection_id):
    """Gets a function from a module based on the user_type, action and collection_id"""
    version_for_module = get_version(version)
    print version_for_module
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


# every call in the API except pending retailers CREATE and LOGIN
@app.route('/v1/<collection_id>/<action>', methods=['GET', 'POST'])
@sec.check_token
def crud_action(headers, collection_id, action):
    print 'HEADERS'
    print str(request.headers)
    user_type = headers[DECODED_TOKEN][USER_TYPE]
    in_data = io_transformers.transform_input(request.data, request.headers, True)
    print '{0} performs {1} on collection {2}'.format(user_type, action, collection_id)
    func = get_func('v1', crud_safety, user_type, action, collection_id)
    out_data = func(collection_id, headers, in_data)
    return io_transformers.transform_output(out_data, request.headers)


# function for login and getting a fresh token every time
@app.route('/v1/sec/<user_type>/<action>', methods=['POST'])
def user_sec_action(user_type, action):
    print 'HEADERS'
    print str(request.headers)
    in_data = io_transformers.transform_input(request.data, request.headers, False)
    print '{0} called sec action {1}'.format(user_type, action)
    func = get_func('v1', sec, user_type, action, None)
    out_data = func(in_data, request.headers)
    return io_transformers.transform_output(out_data, request.headers)


# function for pending_retailers CREATE only
# no security because everyone can sign up to SpotMarket
@app.route('/v1/pending_retailers/create', methods=['POST'])
def pending_retailers_create():
    print 'pending_retailers_create'
    print str(request.headers)
    in_data = io_transformers.transform_input(request.data, request.headers, False)
    print 'retailer tries to sign up in Spot Market'
    func = get_func('v1', pending, 'retailers', 'create', 'pending_retailers')
    out_data = func('pending_retailers', request.headers, in_data)
    return io_transformers.transform_output(out_data, request.headers)


# function for choosing the correct version based on the requested url
def get_version(version):
    switcher = {
        'v1': "",
        'v2': "two",
        'v3': "three",
    }
    return switcher.get(version, "nothing")

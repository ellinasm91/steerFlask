import sys
import json
from FlaskWebProject.steershared.shared_consts import DATA
from datetime import datetime

_default_content_type = 'application_json'


def _transform_input_json(payload, wrap_in_list):
    try:
        print 'PAYLOAD'
        print payload
        transformed_payload = json.loads(payload)
        print 'TRANSFORMED PAYLOAD'
        print transformed_payload
        if wrap_in_list and type(transformed_payload) is not list and type(transformed_payload) is not None:
            transformed_payload = [transformed_payload]
        return transformed_payload
    except ValueError:  # If no json object can be decoded then return None
        return None


# TODO: Catch TypeError because DateTime cannot be serialized to JSON
def _transform_output_json(payload):
    # Add empty dictionary for warnings. They are not currently used but we have included them in API (and
    # documentation) to make it easier to add them later
    print payload
    if type(payload) is not list:
        payload = [payload]
    try:
        out = json.dumps({DATA: payload, 'warnings': {}})
    except TypeError:
        for doc in payload:
            for k, v in doc.iteritems():
                if type(v) is datetime:
                    doc[k] = str(v)
        out = json.dumps({DATA: payload, 'warnings': {}})
    return out


def _get_func(transform_direction, headers):
    current_module = sys.modules[__name__]
    return getattr(current_module, '_transform_{0}_{1}'.format(transform_direction, 'json'))


def transform_input(payload, headers, wrap_in_list):
    func = _get_func('input', headers)
    return func(payload, wrap_in_list)


def transform_output(payload, headers):
    func = _get_func('output', headers)
    return func(payload)

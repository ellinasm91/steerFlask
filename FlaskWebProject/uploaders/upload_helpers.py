from FlaskWebProject.steershared.shared_consts import DECODED_TOKEN, USER_TYPE, DEV, ID, MODE_HEADER_KEY, DEBUG


def get_dev_headers(mode=DEBUG):
    print mode
    return {DECODED_TOKEN: {USER_TYPE: DEV, ID: 'developer'}, MODE_HEADER_KEY: mode}

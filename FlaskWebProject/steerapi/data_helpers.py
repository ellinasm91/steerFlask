from FlaskWebProject.steershared.shared_consts import MODE_HEADER_KEY, DEBUG


def get_mode(headers):
    try:
        return headers[MODE_HEADER_KEY]
    except KeyError:
        return DEBUG

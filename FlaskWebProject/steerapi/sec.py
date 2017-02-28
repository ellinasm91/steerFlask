import datetime
import hashlib
import random
from functools import wraps

import jwt
from flask import request

import io_transformers
from FlaskWebProject import app
from FlaskWebProject.steershared.shared_consts import *
from FlaskWebProject.steershared.dbconnectors.db_helpers import get_db
from sec_errors import IncorrectLoginError, InvalidTokenError, NoTokenError
import sec_third_party

EXP = 'exp'


def gen_salt():
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars = []
    for i in range(16):
        chars.append(random.choice(alphabet))
    return ''.join(chars)


def gen_hashed_pass(password, salt):
    m = hashlib.sha512()
    m.update(password)
    m.update(salt)
    return m.hexdigest()


def add_to_blacklist_tokens(headers):
    db = get_db(headers)
    blacklist_tokens = db.read(BLACKLIST_TOKENS, None)

    if blacklist_tokens:
        blacklist_tokens[0][BLACKLIST_TOKENS].append(headers[TOKEN_HEADER_KEY])
        db.update(BLACKLIST_TOKENS, blacklist_tokens)
    else:
        blacklist_tokens = {BLACKLIST_TOKENS: [headers[TOKEN_HEADER_KEY]]}
        db.create(BLACKLIST_TOKENS, blacklist_tokens)


def check_token(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            if TOKEN_HEADER_KEY not in request.headers:
                raise NoTokenError()

            blacklist_tokens = get_db(request.headers).read(BLACKLIST_TOKENS, None)

            if blacklist_tokens:
                blacklist_tokens = blacklist_tokens[0][BLACKLIST_TOKENS]
                if request.headers[TOKEN_HEADER_KEY] in blacklist_tokens:
                    raise InvalidTokenError()

            decoded_token = jwt.decode(request.headers[TOKEN_HEADER_KEY], app.config[JWT_SECRET])

            if decoded_token[TOKEN_TYPE] == REFRESH_TOKEN:
                decoded_token[TOKEN_TYPE] = ACCESS_TOKEN
                decoded_token[EXP] = datetime.datetime.now() + datetime.timedelta(hours=24)
                token = jwt.encode(decoded_token, app.config[JWT_SECRET], algorithm=app.config[JWT_ALGO])
                print 'Returning Access Token'
                return io_transformers.transform_output({ACCESS_TOKEN: token}, request.headers)
            else:
                print 'Accessing Resource'
                headers = dict(request.headers)
                headers[DECODED_TOKEN] = decoded_token
                return func(headers, *args, **kwargs)
        except jwt.DecodeError:
            raise InvalidTokenError()

    return func_wrapper


def gen_tokens(user, user_collection):
    print user
    refresh_token = None
    access_token = None
    # There is some duplication in this function, but we should keep it all separate so that we can easily change things
    # e.g. Maybe we want different users tokens to have different expiry periods

    if user_collection == RETAILER_USERS:
        try:
            is_admin = user[IS_ADMIN]
        except KeyError:
            is_admin = False
        refresh_token = jwt.encode({ID: user[ID], RETAILER_ID: user[RETAILER_ID], USER_TYPE: RETAILER,
                                    TOKEN_TYPE: REFRESH_TOKEN,
                                    EXP: datetime.datetime.now() + datetime.timedelta(days=30)},
                                   app.config[JWT_SECRET], algorithm=app.config[JWT_ALGO])
        access_token = jwt.encode({ID: user[ID], IS_ADMIN: is_admin, RETAILER_ID: user[RETAILER_ID],
                                   USER_TYPE: RETAILER, TOKEN_TYPE: ACCESS_TOKEN,
                                   EXP: datetime.datetime.now() + datetime.timedelta(days=30)},
                                  app.config[JWT_SECRET], algorithm=app.config[JWT_ALGO])
    elif user_collection == TOWN_USERS:
        try:
            is_admin = user[IS_ADMIN]
        except KeyError:
            is_admin = False
        refresh_token = jwt.encode({ID: user[ID], USER_TYPE: TOWN, TOKEN_TYPE: REFRESH_TOKEN,
                                    EXP: datetime.datetime.now() + datetime.timedelta(days=30)},
                                   app.config[JWT_SECRET], algorithm=app.config[JWT_ALGO])
        access_token = jwt.encode({ID: user[ID], IS_ADMIN: is_admin, USER_TYPE: TOWN, TOKEN_TYPE: ACCESS_TOKEN,
                                   EXP: datetime.datetime.now() + datetime.timedelta(days=30)},
                                  app.config[JWT_SECRET], algorithm=app.config[JWT_ALGO])
    elif user_collection == CONSUMERS:
        refresh_token = jwt.encode({ID: user[ID], USER_TYPE: CONSUMER, TOKEN_TYPE: REFRESH_TOKEN,
                                    EXP: datetime.datetime.now() + datetime.timedelta(days=30)},
                                   app.config[JWT_SECRET], algorithm=app.config[JWT_ALGO])
        access_token = jwt.encode({ID: user[ID], USER_TYPE: CONSUMER, TOKEN_TYPE: ACCESS_TOKEN,
                                   EXP: datetime.datetime.now() + datetime.timedelta(days=30)},
                                  app.config[JWT_SECRET], algorithm=app.config[JWT_ALGO])
    return refresh_token, access_token


def login_with_password(in_data, user_collection, headers):
    username = in_data[USERNAME]
    password = in_data[PASSWORD]
    users = get_db(headers).read(user_collection, {USERNAME: username})
    if users:
        user = users[0]
        hashed_pass = gen_hashed_pass(password, user[SALT])
        if hashed_pass == user[HASHED_PASS]:
            del user[HASHED_PASS], user[SALT]
            user[REFRESH_TOKEN], user[ACCESS_TOKEN] = gen_tokens(user, user_collection)
            return user
        else:
            raise IncorrectLoginError(username)
    else:
        raise IncorrectLoginError(username)


def retailer_login(in_data, headers):
    user = login_with_password(in_data, RETAILER_USERS, headers)
    try:
        # Find the retailer name
        retailer = get_db(headers).read(RETAILERS, {ID: user[RETAILER_ID]})[0]
        user[RETAILER_NAME] = retailer[NAME]
        user[RETAILER_TYPE] = retailer[RETAILER_TYPE]
        user[ADDRESS] = retailer[ADDRESS]
    # Zen: Errors should never pass silently, unless explicitly silenced. It's not the end of the world if we can't
    # find the retailer name
    except IndexError:
        pass
    except KeyError:
        pass
    return user


def town_login(in_data, headers):
    return login_with_password(in_data, TOWN_USERS, headers)


def find_existing_consumer(db, third_party_name, third_party_consumer_id):
    consumers = db.read(CONSUMERS)
    for consumer in consumers:
        if THIRD_PARTY_TOKENS in consumer.keys():
            # Find the token matching the third_party_name
            for token in consumer[THIRD_PARTY_TOKENS]:
                if (token[THIRD_PARTY_NAME] == third_party_name
                        and token[THIRD_PARTY_USER_ID] == third_party_consumer_id):
                    return consumer
    return None


def consumer_login(in_data, headers):
    db = get_db(headers)
    print 'HEADERS'
    print headers
    print '\nDATA'
    print in_data
    third_party_name = in_data[THIRD_PARTY_NAME]
    print third_party_name
    third_party_user_id = sec_third_party.get_third_party_user_id_from_token(in_data)
    print third_party_user_id

    consumer = find_existing_consumer(db, third_party_name, third_party_user_id)

    if consumer:
        print consumer
        # Update consumer third party access and refresh tokens
        for token in consumer[THIRD_PARTY_TOKENS]:
            if token[THIRD_PARTY_NAME] == third_party_name:
                token[ACCESS_TOKEN] = in_data[ACCESS_TOKEN]
                token[SECRET_TOKEN] = in_data[SECRET_TOKEN]
        db.update(CONSUMERS, [consumer])
    else:
        consumer = {}
        token = {THIRD_PARTY_NAME: third_party_name, THIRD_PARTY_USER_ID: third_party_user_id,
                 ACCESS_TOKEN: in_data[ACCESS_TOKEN], SECRET_TOKEN: in_data[SECRET_TOKEN], LAST_UPDATE_IDS: ''}
        print token
        consumer[THIRD_PARTY_TOKENS] = [token]
        created_consumers = db.create(CONSUMERS, [consumer])
        consumer[ID] = created_consumers[0]

    # Generate SpotMarkets access and refresh tokens
    consumer[REFRESH_TOKEN], consumer[ACCESS_TOKEN] = gen_tokens(consumer, CONSUMERS)

    # Delete fields which should not be exposed to client
    hidden_attrs = [HASHED_PASS, SALT]
    for attr in hidden_attrs:
        try:
            del consumer[attr]
        # Better to ask forgiveness than permission. Zen: Errors should never pass silently, unless explicitly silenced
        except KeyError:
            pass
    return consumer


def consumer_logintemp(in_data, headers):
    return login_with_password(in_data, CONSUMERS, headers)


if __name__ == '__main__':
    dev_headers = {MODE_HEADER_KEY: DEBUG}
    password_ = 'Spot1234'
    dev_retailer = retailer_login({USERNAME: 'JohnDoe', PASSWORD: password_}, dev_headers)
    print 'RETAILER'
    print dev_retailer
    dev_town_user = town_login({USERNAME: 'JoeBloggs', PASSWORD: password_}, dev_headers)
    print 'TOWN_USER'
    print dev_town_user
    dev_consumer = consumer_logintemp({USERNAME: 'Hazza', PASSWORD: password_}, dev_headers)
    print 'CONSUMER'
    print dev_consumer

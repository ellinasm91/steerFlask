import datetime
import hashlib
import random
from copy import deepcopy

import crud_safety
from functools import wraps

import jwt
from flask import request

import io_transformers
from FlaskWebProject import app
from FlaskWebProject.steershared.shared_consts import *
from FlaskWebProject.steershared.dbconnectors.db_helpers import get_db
from sec_errors import IncorrectLoginError, InvalidTokenError, NoTokenError
import sec_third_party

from crud_helpers import *
from data_errors import *
import sec
from operator import itemgetter
# written by C.Pigiotis


# function for adding the data for pending retailers
def create(collection_id, headers, docs):
    if type(docs) is dict:
        docs = [docs]

    # added checks for correct attributes when a retailer signs up
    check_illegal_attrs(collection_id, docs)
    check_missing_attrs(collection_id, docs)
    check_create_unique_attrs(collection_id, headers, docs)

    ids = get_db(headers).create(collection_id, docs)
    return get_id_docs(ids)


# this function gets called from client_urls for pending retailers CREATE
def create_retailer_users(collection_id, headers, docs):
    # hashing the password of the retailer
    for doc in docs:
        salt = sec.gen_salt()
        print type(doc[PASSWORD])
        hashed_pass = sec.gen_hashed_pass(doc[PASSWORD], salt)
        doc[SALT] = salt
        doc[HASHED_PASS] = hashed_pass
        del doc[PASSWORD]
    return create(collection_id, headers, docs)

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

from crud_helpers import *
from data_errors import *
import sec
from operator import itemgetter


def create(collection_id, headers, docs):
    if type(docs) is dict:
        docs = [docs]

    # check_collection_permission(collection_id, headers, CREATE)
    # enforce_principal_ref(collection_id, headers, docs, [])
    # check_illegal_attrs(collection_id, docs)
    # check_missing_attrs(collection_id, docs)
    # check_create_unique_attrs(collection_id, headers, docs)
    ids = get_db(headers).create(collection_id, docs)
    return get_id_docs(ids)


def town_read_pending_retailers(collection_id, headers, query_dicts):
    # check_collection_permission(collection_id, headers, READ)
    # Enforce read safety means that there is no need to check doc permission
    # query_dicts = enforce_read_safety(collection_id, headers, query_dicts)
    docs = get_db(headers).read(PENDING_RETAILERS)
    return docs

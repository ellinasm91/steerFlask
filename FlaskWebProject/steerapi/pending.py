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


ret_list = ['address', 'description', 'email', 'survey_image_url', 'latitude', 'logo_image_url', 'longitude', 'name',
            'phone', 'postcode', 'website']

ret_user_list = ['email', 'firstname', 'password', 'phone', 'surname', 'username']

 # @retailer_id : str
 # @salt : str


def get_ret_doc(docs):
    # if type(docs) is dict:
    #    docs = [docs]
    ret_doc = {}

    # We take all attributes listed in ret_list and add them to a new list to return.
    for attri in ret_list:
        ret_doc[attri] = docs[attri]
    print ret_doc
    if type(ret_doc) is dict:
        ret_doc = [ret_doc]
    return ret_doc


def get_ret_user_doc(docs):
    # if type(docs) is dict:
    #   docs = [docs]
    ret_user_doc = {}
    print ret_user_doc
    # We take all attributes listed in ret_user_doc and add them to a new list to return.
    for attri in ret_user_list:
        ret_user_doc[attri] = docs[attri]
    print ret_user_doc
    if type(ret_user_doc) is dict:
        ret_user_doc = [ret_user_doc]
    return ret_user_doc


def town_approve_pending_retailers(collection_id, headers, in_data):
    print 'approving in progress'
    # Expecting pending retailers id
    pending_ret_id = in_data['id']
    print pending_ret_id
    # Retrieve doc from pending retailers
    try:
        pending_ret_doc = get_db(headers).read(PENDING_RETAILERS, {ID: pending_ret_id})[0]
    except IndexError:
        raise MissingDocsError(CONSUMERS, [pending_ret_doc])

    ret_doc = get_ret_doc(pending_ret_doc)
    print ret_doc
    ret_user_doc = get_ret_user_doc(pending_ret_doc)
    # Create retailer in DB
    ids = get_db(headers).create(RETAILERS, ret_doc)
    # Create retailer admin in DB including the corresponding retailer_id
    for id in ids:
        ret_user_doc[0]['retailer_id'] = id
    ret_user_doc[0]['is_admin'] = True
    # ids2 = get_db(headers).create(RETAILER_USERS, ret_user_doc)
    # on normal system use crud_safety.py
    create_retailer_users(RETAILER_USERS, headers, ret_user_doc)
    delete_after_approval(headers, pending_ret_id)

    return pending_ret_doc


def create_retailer_users(collection_id, headers, docs):

    for doc in docs:
        salt = sec.gen_salt()
        print type(doc[PASSWORD])
        hashed_pass = sec.gen_hashed_pass(doc[PASSWORD], salt)
        doc[SALT] = salt
        doc[HASHED_PASS] = hashed_pass
        del doc[PASSWORD]
    return create(collection_id, headers, docs)


def delete_after_approval(headers,delete_ids):
    print 'Deleting pending retailer'
    # return crud_safety.delete(PENDING_RETAILERS, headers, delete_ids)
    return get_db(headers).delete(PENDING_RETAILERS, str(delete_ids))

import json
from FlaskWebProject.steerapi import sec, crud_safety
from FlaskWebProject.steershared.dbconnectors.db_helpers import get_db
from FlaskWebProject.steershared.shared_consts import *
from upload_helpers import get_dev_headers

_mode = TEST

db = get_db(_mode)

_retailer_users = [{USERNAME: 'Veggie', FIRSTNAME: 'Veggie', SURNAME: 'Veggie', EMAIL: 'veggie@vegboxcafe.com',
                    PHONE: '07777777777', IS_ADMIN: True},
                   {USERNAME: 'JohnDoe', FIRSTNAME: 'John', SURNAME: 'Doe', EMAIL: 'johndoe@vegboxcafe.com',
                    PHONE: '07777777777', IS_ADMIN: True}]


_town_users = [{USERNAME: 'JoeBloggs', FIRSTNAME: 'Joe', SURNAME: 'Bloggs', EMAIL: 'joebloggs@kcc.gov',
                PHONE: '07777777777'}]


_consumers = [{USERNAME: "Bonobo", FIRSTNAME: "Tom", SURNAME: "Mulvaney", GENDER: "Male", DOB: "08/11/89",
               POSTCODE: "CT1 1AA", ADDRESS: "1 Nackington Road,Canterbury,UK", EMAIL: "ucabtfm@ucl.ac.uk",
               THIRD_PARTY_TOKENS: []},
              {USERNAME: "Hazza", FIRSTNAME: "Harry", SURNAME: "Blum", GENDER: "Male", DOB: "01/01/93",
               POSTCODE: "CT1 1AA", ADDRESS: "1 Nackington Road,Canterbury,UK", EMAIL: "ucabhco@ucl.ac.uk",
               THIRD_PARTY_TOKENS: []},
              {USERNAME: "JoeBloggs", FIRSTNAME: "Joe", SURNAME: "Bloggs", GENDER: "Male", DOB: "01/01/93",
               POSTCODE: "CT1 1BB", ADDRESS: "70 Northgate,Canterbury,UK", EMAIL: "ucabhco@ucl.ac.uk",
               THIRD_PARTY_TOKENS: []}]


def gen_salt_and_hashed_pass(user):
    salt = sec.gen_salt()
    hashed_pass = sec.gen_hashed_pass('Spot1234', salt)
    user[HASHED_PASS] = hashed_pass
    user[SALT] = salt


def create_all_retailer_users():
    retailer_user = {FIRSTNAME: 'Admin', IS_ADMIN: True}

    headers = get_dev_headers(TEST)

    retailers = db.read(RETAILERS)
    for retailer in retailers:
        retailer_user[RETAILER_ID] = retailer[ID]
        retailer_user[USERNAME] = retailer[NAME] + ' Admin'
        gen_salt_and_hashed_pass(retailer_user)
        try:
            crud_safety.create(RETAILER_USERS, headers, [retailer_user])
        except Exception as e:
            print type(e)
            print e
            raise e


def create_retailer_user():
    retailer_name = 'The Veg Box Cafe'
    #retailers = db.read(RETAILERS, {NAME: retailer_name})
    retailers = db.read(RETAILERS, {WEBSITE: 'http://www.thevegboxcafe.co.uk'})
    retailer_id = retailers[0][ID]
    for retailer_user in _retailer_users:
        retailer_user[RETAILER_ID] = retailer_id
        gen_salt_and_hashed_pass(retailer_user)
    created_ids = crud_safety.create(RETAILER_USERS, get_dev_headers(_mode), _retailer_users)
    return json.dumps(created_ids)


def create_consumers():
    for consumer in _consumers:
        gen_salt_and_hashed_pass(consumer)
    created_ids = db.create(CONSUMERS, _consumers)
    return json.dumps(created_ids)


def create_town_user():
    for town_user in _town_users:
        gen_salt_and_hashed_pass(town_user)
    created_ids = db.create(TOWN_USERS, _town_users)
    return json.dumps(created_ids)


if __name__ == '__main__':
    db.delete(CONSUMERS)
    docs = db.read(CONSUMERS)
    print docs
    create_consumers()

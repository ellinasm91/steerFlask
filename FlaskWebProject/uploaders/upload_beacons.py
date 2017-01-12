from FlaskWebProject.steershared.shared_consts import *
from FlaskWebProject.steershared.dbconnectors.db_helpers import get_db


def upload(mode):
    db = get_db(mode)
    retailer = db.read(RETAILERS, {NAME: 'The Veg Box Cafe'}, DEBUG)[0]

    beacon = {BEACON_TYPE: 'door', IS_ACTIVE: True, MAJOR: 'abc', MINOR: 'def', RETAILER_ID: retailer[ID]}
    db.create(BEACONS, beacon, DEBUG)


if __name__ == '__main__':
    upload()

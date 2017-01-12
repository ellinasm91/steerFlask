# -*- coding: utf-8 -*-

import json
import copy

from FlaskWebProject.steerapi import crud_safety
from FlaskWebProject.steershared.shared_consts import *
from FlaskWebProject.steershared.dbconnectors.db_helpers import get_db
from upload_helpers import get_dev_headers


def upload_retailers(mode):
    retailers = None
    with open('retailers.json', 'r') as myfile:
        raw_retailer_data = myfile.read()
        retailers = json.loads(raw_retailer_data)

    products = None
    with open('products.json', 'r') as myfile:
        raw_product_data = myfile.read()
        products = json.loads(raw_product_data)

    headers = get_dev_headers(mode)

    for retailer in list(retailers):
        retailer_products = copy.deepcopy([product for product in products if product[RETAILER_NAME] == retailer[NAME]])
        if not retailer_products:
            retailers.remove(retailer)

    ids = crud_safety.create(RETAILERS, headers, retailers)
    print ids


def upload_products(mode):
    db = get_db(mode)
    retailers = db.read(RETAILERS)

    products = None
    with open('products.json', 'r') as myfile:
        raw_product_data = myfile.read()
        products = json.loads(raw_product_data)

    headers = get_dev_headers(mode)
    print headers

    for retailer in retailers:
        retailer_products = copy.deepcopy([product for product in products if product[RETAILER_NAME] == retailer[NAME]])

        if retailer_products:
            print '{0}: {1}'.format(retailer[NAME], retailer[ID])
            headers[DECODED_TOKEN][USER_TYPE] = RETAILER
            headers[DECODED_TOKEN][RETAILER_ID] = retailer[ID]
            for product in retailer_products:
                product[RETAILER_ID] = retailer[ID]
                product[IS_FILE_UPLOAD] = True
                product[RETAILER_NAME]
            try:
                ids = crud_safety.create_products(PRODUCTS, headers, retailer_products)
            except Exception as e:
                print e
                print retailer
                print retailer_products
                raise e


if __name__ == '__main__':
    mode = TEST
    db = get_db(mode)
    db.delete(RETAILERS)
    db.delete(PRODUCTS)
    upload_retailers(mode)
    upload_products(mode)

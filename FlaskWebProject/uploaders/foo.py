# -*- coding: utf-8 -*-

import json
import re

from FlaskWebProject.steershared.dbconnectors.db_helpers import get_db
from FlaskWebProject.steershared.shared_consts import *
from operator import itemgetter

db = get_db(DEBUG)


def modify_consumers():
    consumers = db.read(CONSUMERS, {USERNAME: 'Hazza'})
    consumer_id = consumers[0][ID]
    recommendations = db.read(RECOMMENDATIONS)
    for recommendation in recommendations:
        recommendation[CONSUMER_ID] = consumer_id
    db.update(RECOMMENDATIONS, recommendations)


def modify_retailer_users():
    retailers = db.read(RETAILERS, {NAME: 'The Veg Box Cafe'})
    retailer_users = db.read(RETAILER_USERS, {USERNAME: 'JohnDoe'})
    for retailer_user in retailer_users:
        retailer_user[RETAILER_ID] = retailers[0][ID]
    db.update(RETAILER_USERS, retailer_users)


def update_ratings():
    ratings = db.read(RATINGS)
    retailers = db.read(RETAILERS)
    products = db.read(PRODUCTS)
    for rating in ratings:
        if rating[NAME] == 'Upper Lip Treatment':
            rating[NAME] = 'Treatments Upper Lip'
        if rating[NAME] == 'Eyebrow Treatment':
            rating[NAME] = 'Treatments Eyebrows'
        """
        for retailer in retailers:
            if retailer[NAME] == rating[RETAILER_NAME]:
                rating[RETAILER_ID] = retailer[ID]

        for product in products:
            if product[NAME] == rating[NAME] and product[RETAILER_ID] == rating[RETAILER_ID]:
                rating[ITEM_ID] = product[ID]
        """
    db.update(RATINGS, ratings)


def modify_interactions():
    collection_id = OFFER_INTERACTIONS
    interactions = db.read(collection_id)
    for interaction in interactions:
        interaction[SENTIMENT] = interaction[VALUE]
    db.update(collection_id, interactions)


def modify_products_file():
    products = None
    with open('products.json', 'r') as myfile:
        raw_product_data = myfile.read()
        products = json.loads(raw_product_data)

    print products

    for product in products:
        product[PRICE] = product[PRICE].replace(u'£', u'').replace('n/a', '-1').replace(',', '').replace('From ', '').\
            replace('From: ', '').replace(' / 15 sachets', '').replace('from just ', '').replace('from ', '')
        product[PRICE] = product[PRICE].strip()

        if not product[PRICE]:
            product[PRICE] = '-1'

        full_hyphen_pattern = '[0-9]+-[0-9]+'
        half_hyphen_pattern = '[0-9]+-'
        print product[PRICE]
        if re.match(full_hyphen_pattern, product[PRICE]):
            try:
                half_match = re.match(half_hyphen_pattern, product[PRICE])
                product[PRICE] = re.sub(full_hyphen_pattern, half_match.group(0), product[PRICE]).replace('-', '')
            except Exception as e:
                print e
                print product[PRICE]
                raise e
        try:
            product[PRICE] = float(product[PRICE])
        except Exception as e:
            print e
            print product
            print product[PRICE]
            raise e

    print products

    with open('products.json', 'w') as myfile:
        myfile.write(json.dumps(products))


def modify_retailers_file():
    retailers = None
    with open('retailers.json', 'r') as myfile:
        raw_product_data = myfile.read()
        retailers = json.loads(raw_product_data)
        rename_attrs = {TYPE: RETAILER_TYPE, 'logo_image': LOGO_IMAGE_URL, 'store_image': SURVEY_IMAGE_URL}
    for retailer in retailers:
        for old_attr, new_attr in rename_attrs.iteritems():
            retailer[new_attr] = retailer[old_attr]
            del retailer[old_attr]
        retailer[ADDRESS] = '{0}, {1}'.format(retailer[ADDRESS], retailer['region'])
        del retailer['region']

    with open('retailers.json', 'w') as myfile:
        myfile.write(json.dumps(retailers))


if __name__ == '__main__':
    db = get_db(EVAL)
    ratings = db.read(RATINGS)
    consumer_ids = {ID: ratings[CONSUMER_ID] for rating in ratings}
    print consumer_ids
    product_ids = {ID: ratings[PRODUCT_ID] for rating in ratings}
    print product_ids

    consumers = db.read(CONSUMERS, consumer_ids)
    print len(consumers)

    products = db.read(PRODUCTS, product_ids)
    print len(products)

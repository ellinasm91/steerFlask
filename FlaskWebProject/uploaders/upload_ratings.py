from upload_helpers import get_dev_headers
from FlaskWebProject.steerapi import crud_safety
from FlaskWebProject.steershared.shared_consts import *
import random

headers = get_dev_headers()


def upload_predictions(consumers, retailer_names, is_prediction):
    query_dicts = [{NAME: retailer_name} for retailer_name in retailer_names]
    retailers = crud_safety.read(RETAILERS, headers, query_dicts)
    retailer_ids = [{RETAILER_ID: retailer[ID]} for retailer in retailers]

    for consumer in consumers:
        query_dicts = [{RETAILER_NAME: retailer_name, CONSUMER_ID: consumer[ID],
                        IS_PREDICTION: is_prediction} for retailer_name in retailer_names]

    ratings = crud_safety.read(RATINGS, headers, query_dicts)

    delete_ids = [rating[ID] for rating in ratings]

    crud_safety.delete(RATINGS, headers, delete_ids)

    products = crud_safety.read(PRODUCTS, headers, retailer_ids)

    for product in products:
        for retailer in retailers:
            if retailer[ID] == product[RETAILER_ID]:
                product[RETAILER_NAME] = retailer[NAME]

    ratings = []
    for consumer in consumers:
        for product in products:
            rating = {CONSUMER_ID: consumer[ID], PRODUCT_ID: product[ID], ITEM_TYPE: PRODUCTS, NAME: product[NAME],
                      PRICE: product[PRICE], RETAILER_ID: product[RETAILER_ID], RETAILER_NAME: product[RETAILER_NAME],
                      IS_PREDICTION: is_prediction, IMAGE_FILENAMES: "", SENTIMENT: random.uniform(0.2, 0.8),
                      SURVEY_IMAGE_URL: product[SURVEY_IMAGE_URL]}
            ratings.append(rating)
    crud_safety.create(RATINGS, headers, ratings)


if __name__ == '__main__':
    consumers_ = crud_safety.read(CONSUMERS, headers, {EMAIL: 'gsavvas3@gmail.com'})
    print consumers_
    upload_predictions(consumers_, ['The Unicorn Inn', 'The Veg Box Cafe', 'Moss'], True)

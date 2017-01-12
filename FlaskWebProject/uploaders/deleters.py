from FlaskWebProject.steershared.dbconnectors.db_helpers import get_db
from FlaskWebProject.steershared.shared_consts import *

db = get_db(DEBUG)

def delete_products():
    products = db.read(PRODUCTS)
    print products
    products = [product for product in products if IMAGE_URL in product.keys() and 'http' in product[IMAGE_URL]]
    print products
    delete_ids = [product[ID] for product in products]
    print delete_ids
    db.delete(PRODUCTS, delete_ids)
    products = db.read(PRODUCTS)
    print products


def delete_retailers():
    retailers = db.read(RETAILERS)
    print retailers
    retailers = [retailer for retailer in retailers if NAME not in retailer.keys()]
    delete_ids = [retailer[ID] for retailer in retailers]
    db.delete(RETAILERS, delete_ids)
    retailers = db.read(RETAILERS)
    print retailers


def delete(collection_id, delete_ids=None):
    if delete_ids is None:
        docs = db.read(collection_id)
        delete_ids = [doc[ID] for doc in docs]
    db.delete(collection_id, delete_ids)
    docs = db.read(collection_id)
    print docs


if __name__ == '__main__':
    delete(RETAILERS, '57c56f345c92eb20cc0e0d3d')

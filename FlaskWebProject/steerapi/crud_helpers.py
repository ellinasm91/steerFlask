from FlaskWebProject.steershared.dbconnectors.db_helpers import get_db
from FlaskWebProject.steershared.shared_consts import *
from FlaskWebProject.steershared.textclassifier import text_classifier
from data_errors import *
from sec_errors import NoDocumentPermissionError, NoCollectionPermissionError, UnknownUserTypeError
import math
#import numpy as np
from random import randint


def classify_products_kmeans(headers, products):
    return
    db = get_db(headers)

    try:
        center_points = db.read(KMEANS_CATEGORIES)[0][CENTER_POINTS]
    except IndexError:
        return
    center_points = np.asarray(center_points)

    for idx, product in enumerate(products):
        # The schema of the KMEANS_CATEGORIES collection was changed, and this code broke
        try:
            product = {k: v for k, v in product.iteritems() if k in KMEANS_FEATURES}
            product[INTERACTIONS] = 0
            products[idx][QUANTITY] = randint(1, 100)
            min_distance = -1
            category = None
            cur_category = 0
            print center_points
            for center_v in center_points:
                print type(center_v)
                print center_v
                if len(center_v) != len(product):
                    break  # Product is missing attrs needed to cluster
                else:
                    distance = 0
                    for i in range(len(center_v)):
                        distance += (product[product.keys()[i]] - center_v[i]) ** 2
                    distance = math.sqrt(distance)
                    if distance < min_distance:
                        min_distance = distance
                        category = cur_category
                    cur_category += 1
            products[idx][KMEANS_CATEGORY_ID] = category
        except:
            products[idx][KMEANS_CATEGORY_ID] = None


def classify_products_iab(headers, products):
    db = get_db(headers)
    categories = db.read(IAB_CATEGORIES)
    for idx, product in enumerate(products):
        print 'Classifying {0} / {1}'.format(idx, len(products))
        iab_category = text_classifier.get_category(product[NAME])
        if not iab_category:
            try:
                iab_category = text_classifier.get_category('{0} {1}'.format(product[NAME], product[DESCRIPTION]))
            except KeyError:  # If the product doesn't have a description then we get a KeyError
                pass
        product[IAB_CATEGORY_CODE] = iab_category
        for category in categories:
            if category[CATEGORY_CODE] == iab_category:
                product[IAB_CATEGORY_ID] = category[ID]
                break


def get_id_docs(ids):
    return [{ID: id_} for id_ in ids]


def check_missing_attrs(collection_id, docs):
    if collection_id in MANDATORY_ATTRS.keys():
        for doc in docs:
            missing_attrs = [attr for attr in MANDATORY_ATTRS[collection_id] if attr not in doc]
            if missing_attrs:
                id_ = doc[ID] if ID in doc else UNKNOWN_ID
                print '{0} coll missing attrs: {1}'.format(collection_id, missing_attrs)
                raise MissingAttrError(id_, collection_id, missing_attrs)


def check_illegal_attrs(collection_id, docs):
    if collection_id in LEGAL_ATTRS.keys():
        for doc in docs:
            illegal_attrs = [attr for attr in doc if attr not in LEGAL_ATTRS[collection_id]]
            if illegal_attrs:
                id_ = doc[ID] if ID in doc else UNKNOWN_ID
                print '{0} coll illegal attrs: {1}'.format(collection_id, illegal_attrs)
                raise IllegalAttrError(id_, collection_id, illegal_attrs)


def check_create_unique_attrs(collection_id, headers, docs):
    if collection_id in UNIQUE_ATTRS.keys():
        db = get_db(headers)
        existing_docs = db.read(collection_id)
        for doc in docs:
            for attr in UNIQUE_ATTRS[collection_id]:
                try:
                    if any(doc[attr] == existing_doc[attr] for existing_doc in existing_docs):
                        raise NonUniqueAttrError(collection_id, attr, doc[attr])
                except KeyError:
                    pass


def check_missing_docs(collection_id, request_ids, found_ids):
    missing_ids = [id_ for id_ in request_ids if id_ not in found_ids]
    if missing_ids:
        raise MissingDocsError(collection_id, missing_ids)


def has_principal_ref(collection_id, headers):
    """Check if docs  in the collection have a reference to the principal accessing the resource"""
    user_type = headers[DECODED_TOKEN][USER_TYPE]
    # Check if (collection_id, user_type) combination requires reference to the user
    # Fail-safe defaults: Base access decisions on permission rather than exclusion
    if user_type == CONSUMER:
        return collection_id in [RATINGS, RECOMMENDATIONS, BEACON_INTERACTIONS, PRODUCT_INTERACTIONS,
                                 OFFER_INTERACTIONS, RETAILER_INTERACTIONS]
    elif user_type == RETAILER:
        return collection_id in [BEACONS, RETAILER_USERS, PRODUCTS, OFFERS, RATINGS, RECOMMENDATIONS,
                                 BEACON_INTERACTIONS, PRODUCT_INTERACTIONS, OFFER_INTERACTIONS, RETAILER_INTERACTIONS]
    elif user_type == TOWN:
        return False
    elif user_type == DEV:
        return False
    else:
        raise UnknownUserTypeError(collection_id, user_type)


def get_principal_ref(headers):
    decoded_token = headers[DECODED_TOKEN]
    principal_ref_attr = decoded_token[USER_TYPE] + '_id'
    principal_id = decoded_token[RETAILER_ID] if decoded_token[USER_TYPE] == RETAILER else decoded_token[ID]
    return principal_ref_attr, principal_id


def enforce_principal_ref(collection_id, headers, new_docs, existing_docs):
    """Enforces safety when writing (creating, updating and deleting)"""
    use_principal_ref = has_principal_ref(collection_id, headers)
    principal_ref_attr, principal_id = get_principal_ref(headers)

    if use_principal_ref:
        for new_doc in new_docs:
            new_doc[principal_ref_attr] = principal_id

        for existing_doc in existing_docs:
            if existing_doc[principal_ref_attr] != principal_id:
                raise NoDocumentPermissionError('perform action', existing_doc, collection_id)


def enforce_read_safety(collection_id, headers, query_dicts):
    """Enforces safety when reading"""
    if has_principal_ref(collection_id, headers):
        principal_ref_attr, principal_id = get_principal_ref(headers)
        if query_dicts is None:
            query_dicts = [{principal_ref_attr: principal_id}]
        else:
            for query_dict in query_dicts:
                query_dict[principal_ref_attr] = principal_id
    return query_dicts


def check_collection_permission(collection_id, headers, action):
    """Check if a user_type has permission to perform a specific action on a specific collection. Example, consumers
    are able to read recommendations, but not able to write recommendations"""
    user_type = headers[DECODED_TOKEN][USER_TYPE]
    # Consumers
    if user_type == CONSUMER:
        # Consumers: Create
        if action == CREATE and collection_id in [PRODUCT_INTERACTIONS, OFFER_INTERACTIONS, RETAILER_INTERACTIONS,
                                                  BEACON_INTERACTIONS, THIRD_PARTY_INTERACTIONS]:
            return
        # Consumers: Read
        elif action == READ and collection_id in [RECOMMENDATIONS, RETAILERS, RATINGS, OFFERS, CONSUMERS]:
            return
        # Consumers: Update, Delete
        elif action in [UPDATE, DELETE] and collection_id == CONSUMERS:
            return
    # Retailers
    elif user_type == RETAILER:
        # Retailers: Create, Update, Delete
        if action in [CREATE, UPDATE, DELETE] and collection_id in [BEACONS, PRODUCTS, OFFERS, RETAILER_USERS,
                                                                    PRODUCT_INTERACTIONS, OFFER_INTERACTIONS]:
            return
        # Retailers: Read
        elif action == READ and collection_id in [BEACONS, CATEGORIES, PRODUCTS, OFFERS, RETAILER_USERS,
                                                  PRODUCT_INTERACTIONS, OFFER_INTERACTIONS, RETAILER_INTERACTIONS,
                                                  BEACON_INTERACTIONS]:
            return
    # Town Users
    elif user_type == TOWN:
        # Town: Create, Update, Delete
        if action in [CREATE, UPDATE, DELETE] and collection_id in [BEACONS, CONSUMERS, RETAILERS, RETAILER_USERS,
                                                                    TOWN_USERS, PENDING_RETAILERS]:
            return
        elif action == READ:
            return
    elif user_type == DEV:
        return
    # Fail-safe defaults: Base access decisions on permission rather than exclusion
    raise NoCollectionPermissionError(user_type, action, collection_id)


def clean_docs(docs):
    """Removes keys from docs which have single leading underscore because these are used by database technologies
    (like DocumentDB) for internal use"""
    return [{key: value for key, value in doc.items() if key[0] != '_'} for doc in docs]


if __name__ == '__main__':
    modes = [EVAL]
    for mode in modes:
        db_ = get_db(mode)
        products_ = db_.read(PRODUCTS)
        categories_ = db_.read(IAB_CATEGORIES)
        for product_ in products_:
            for category_ in categories_:
                if category_[CATEGORY_CODE] == product_[IAB_CATEGORY_CODE]:
                    product_[IAB_CATEGORY_ID] = category_[ID]
                    break
        print products_
        db_.update(PRODUCTS, products_)

    """
    db_ = get_db(DEBUG)

    products_ = db_.read(PRODUCTS)
    center_points_ = db_.read(KMEANS_CATEGORIES)[0][CENTER_POINTS]
    center_points_ = np.asarray(center_points_)

    for product_ in products_:
        interactions = db_.read(PRODUCT_INTERACTIONS, {PRODUCT_ID: product_[ID]})
        product_[INTERACTIONS] = len(interactions)

    products_ = classify_products_kmeans(DEBUG, products_)
    print products_
    db_.update(PRODUCTS, products_)
    """
    """
    print 'Classifying iab products'
    classify_products_iab(products)
    print 'Updating products'
    update_ids = db.update(PRODUCTS, products)
    print 'Complete'
    print update_ids
    """
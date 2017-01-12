from FlaskWebProject.steershared.sentianalysis import sent_analysis
from crud_helpers import *
from data_errors import *
import sec
from FlaskWebProject.steershared.shared_consts import *
from FlaskWebProject.steershared.dbconnectors.db_helpers import get_db
import random
from operator import itemgetter


def create(collection_id, headers, docs):
    if type(docs) is dict:
        docs = [docs]

    check_collection_permission(collection_id, headers, CREATE)
    enforce_principal_ref(collection_id, headers, docs, [])
    check_illegal_attrs(collection_id, docs)
    check_missing_attrs(collection_id, docs)
    check_create_unique_attrs(collection_id, headers, docs)
    ids = get_db(headers).create(collection_id, docs)
    return get_id_docs(ids)


def create_consumer_beacon_interactions(collection_id, headers, interactions):
    for interaction in interactions:
        try:
            beacon = get_db(headers).read(BEACONS, {MAJOR: interaction[MAJOR], MINOR: interaction[MINOR]})[0]
            interaction[RETAILER_ID] = beacon[RETAILER_ID]
            interaction[BEACON_ID] = beacon[ID]
        except IndexError:
            interaction[RETAILER_ID] = UNKNOWN_ID
            interaction[BEACON_ID] = UNKNOWN_ID
    create(collection_id, headers, interactions)


def create_retailer_users(collection_id, headers, docs):
    for doc in docs:
        salt = sec.gen_salt()
        hashed_pass = sec.gen_hashed_pass(doc[PASSWORD], salt)
        doc[SALT] = salt
        doc[HASHED_PASS] = hashed_pass
        del doc[PASSWORD]
    return create(collection_id, headers, docs)


def create_town_users(collection_id, headers, docs):
    for doc in docs:
        salt = sec.gen_salt()
        hashed_pass = sec.gen_hashed_pass(doc[PASSWORD], salt)
        doc[SALT] = salt
        doc[HASHED_PASS] = hashed_pass
        del doc[PASSWORD]
    return create(collection_id, headers, docs)


def consumer_create(collection_id, headers, interactions):
    # If the interaction is for a product, offer or retailer and it has a comment then find the sentiment of the comment
    if collection_id in [PRODUCT_INTERACTIONS, OFFER_INTERACTIONS, RETAILER_INTERACTIONS]:
        for interaction in interactions:
            if COMMENT in interaction.keys() and interaction[COMMENT]:
                interaction[SENTIMENT] = sent_analysis.get_sentiment(interaction[COMMENT])
    return create(collection_id, headers, interactions)


def create_products(collection_id, headers, products):
    db = get_db(headers)

    # Delete previous file uploads if this is a file upload_predictions
    if IS_FILE_UPLOAD not in products[0].keys():
        raise MissingAttrError(products[0][ID], collection_id, IS_FILE_UPLOAD)
    if products[0][IS_FILE_UPLOAD]:
        _, retailer_id = get_principal_ref(headers)
        # Delete existing file upload_predictions products
        deletable_products = db.read(PRODUCTS, {RETAILER_ID: retailer_id,
                                                IS_FILE_UPLOAD: True})

        updatable_products = []
        for delete_product in list(deletable_products):  # Iterate over copy so we can remove while iterating
            for product in products:
                if product[NAME] == delete_product[NAME]:
                    product[ID] = delete_product[ID]
                    updatable_products.append(product)
                    deletable_products.remove(delete_product)
                    break

        if deletable_products:
            delete_ids = [delete_product[ID] for delete_product in deletable_products]
            db.delete(collection_id, delete_ids)
        if updatable_products:
            db.update(collection_id, updatable_products)

    classify_products_kmeans(headers, products)

    # Classify the iab category
    classify_products_iab(headers, products)

    return create(collection_id, headers, products)


def read(collection_id, headers, query_dicts):
    if type(query_dicts) is dict:
        query_dicts = [query_dicts]

    check_collection_permission(collection_id, headers, READ)
    # Enforce read safety means that there is no need to check doc permission
    query_dicts = enforce_read_safety(collection_id, headers, query_dicts)
    docs = get_db(headers).read(collection_id, query_dicts)
    docs = clean_docs(docs)
    return docs


def read_recommendations(collection_id, headers, geo_coordinates):
    query_dicts = [{IS_PREDICTION: True}]
    docs = read(RATINGS, headers, query_dicts)

    if docs:
        docs = sorted(docs, key=itemgetter(SENTIMENT), reverse=True)
        for doc in docs:
            print '{0}: {1}'.format(doc[NAME], doc[SENTIMENT])
    else:
        db = get_db(headers)
        docs = db.read(PRODUCTS)
        for doc in docs:
            doc[SENTIMENT] = random.uniform(0.2, 0.8)
            doc[PRODUCT_ID] = doc[ID]
            del doc[ID]
            _, consumer_id = get_principal_ref(headers)
            doc[CONSUMER_ID] = consumer_id
            doc[ITEM_TYPE] = PRODUCTS
            doc[IS_PREDICTION] = True

    # TODO: Filter based on consumer location
    print docs
    return docs


def consumer_read_retailers(collection_id, headers, geo_coordinates):
    docs = read(collection_id, headers, None)
    # TODO: Filter based on consumer location
    return docs


def update(collection_id, headers, docs):
    if type(docs) is dict:
        docs = [docs]

    check_collection_permission(collection_id, headers, UPDATE)

    update_ids = [doc[ID] for doc in docs]

    # Check that user has permissions for docs with those ids
    query_dicts = [{ID: update_id} for update_id in update_ids]
    existing_docs = read(collection_id, headers, query_dicts)

    enforce_principal_ref(collection_id, headers, docs, existing_docs)
    check_illegal_attrs(collection_id, docs)

    print existing_docs

    if collection_id in UNIQUE_ATTRS.keys():
        for doc in docs:
            print doc
            for attr in UNIQUE_ATTRS[collection_id]:
                try:
                    if any(attr in existing_doc.keys()
                           and doc[attr] == existing_doc[attr]
                           and doc[ID] != existing_doc[ID]
                           for existing_doc in existing_docs):
                        raise NonUniqueAttrError(collection_id, attr, doc[attr])
                except KeyError:
                    pass

    found_ids = get_db(headers).update(collection_id, docs)
    check_missing_docs(collection_id, update_ids, found_ids)
    return get_id_docs(found_ids)


def update_retailer_users(collection_id, headers, docs):
    for doc in docs:
        salt = sec.gen_salt()
        hashed_pass = sec.gen_hashed_pass(doc[PASSWORD], salt)
        doc[SALT] = salt
        doc[HASHED_PASS] = hashed_pass
        del doc[PASSWORD]
    return create(collection_id, headers, docs)


def update_retailers(collection_id, headers, retailers):
    return_docs = []
    for retailer in retailers:
        return_docs.extend(update(collection_id, headers, [retailer]))
        ratings = read(RATINGS, headers, {RETAILER_ID: retailer[ID]})
        for rating in ratings:
            rating[RETAILER_NAME] = retailer[NAME]
        get_db(headers).update(RATINGS, ratings)
    return return_docs


def delete(collection_id, headers, delete_ids):
    if type(delete_ids) is str:
        delete_ids = [delete_ids]

    check_collection_permission(collection_id, headers, DELETE)

    # Check that user has permissions for docs with those ids
    query_dicts = [{ID: delete_id} for delete_id in delete_ids]
    existing_docs = read(collection_id, headers, query_dicts)
    enforce_principal_ref(collection_id, headers, [], existing_docs)
    found_ids = get_db(headers).delete(collection_id, delete_ids)
    check_missing_docs(collection_id, delete_ids, found_ids)
    return get_id_docs(found_ids)


def delete_doc_and_reference_docs(collection_id, headers, delete_ids, reference_key, reference_collections):
    db = get_db(headers)
    return_docs = []
    for delete_id in delete_ids:
        return_docs.extend(delete(collection_id, headers, [delete_id]))
        for reference_collection in reference_collections:
            reference_docs = db.read(reference_collection, {reference_key: delete_id})
            reference_ids = [reference_doc[ID] for reference_doc in reference_docs]
            db.delete(reference_collection, reference_ids)
    return return_docs


def delete_consumers(collection_id, headers, consumer_ids):
    deleted_ids = delete_doc_and_reference_docs(collection_id, headers, consumer_ids, CONSUMER_ID,
                                                [PRODUCT_INTERACTIONS, OFFER_INTERACTIONS, BEACON_INTERACTIONS,
                                                 RETAILER_INTERACTIONS])
    if headers[DECODED_TOKEN][USER_TYPE] == CONSUMER:
        sec.add_to_blacklist_tokens(headers)
    return deleted_ids


def delete_retailers(collection_id, headers, retailer_ids):
    return delete_doc_and_reference_docs(collection_id, headers, retailer_ids, RETAILER_ID, [BEACONS, PRODUCTS, OFFERS,
                                                                                             RETAILER_USERS])


def delete_products(collection_id, headers, product_ids):
    db = get_db(headers)
    updatable_offers = set()
    _, retailer_id = get_principal_ref(headers)
    retailer_offers = db.read(OFFERS, {RETAILER_ID: retailer_id})
    for product_id in product_ids:
        for offer in retailer_offers:
            if offer[PRODUCT_IDS] and product_id in offer[PRODUCT_IDS]:
                offer[PRODUCT_IDS].remove(product_id)
                updatable_offers.add(offer)
    db.update(OFFERS, updatable_offers)
    return delete(collection_id, headers, product_ids)


def add_tokens_consumers(collection_id, headers, docs):
    consumer_id = headers[DECODED_TOKEN][ID]
    try:
        consumer = get_db(headers).read(CONSUMERS, {ID: consumer_id})[0]
    except IndexError:
        raise MissingDocsError(CONSUMERS, [consumer_id])
    for doc in docs:
        doc[LAST_UPDATE_IDS] = ''
    consumer[THIRD_PARTY_TOKENS].extend(docs)
    print consumer
    return update(CONSUMERS, headers, [consumer])


def delete_tokens_consumers(collection_id, headers, docs):
    db = get_db(headers)
    consumer_id = headers[DECODED_TOKEN][ID]
    try:
        consumer = db.read(CONSUMERS, {ID: consumer_id})[0]
        for doc in docs:
            consumer[THIRD_PARTY_TOKENS] = ([token for token in consumer[THIRD_PARTY_TOKENS]
                                             if token[THIRD_PARTY_NAME] != doc[THIRD_PARTY_NAME]])

            # Delete consumer_third_party_interactions and calendar_events
            delete_collection_ids = [THIRD_PARTY_INTERACTIONS, CALENDAR_EVENTS]
            for delete_collection_id in delete_collection_ids:
                delete_docs = db.read(THIRD_PARTY_INTERACTIONS, {CONSUMER_ID: consumer_id,
                                                                 THIRD_PARTY_NAME: doc[THIRD_PARTY_NAME]})
                delete_ids = [{ID: delete_doc[ID] for delete_doc in delete_docs}]
                db.delete(delete_collection_id, delete_ids)
        return update(CONSUMERS, headers, [consumer])
    except IndexError:
        raise MissingDocsError(CONSUMERS, [consumer_id])


def read_bypass(collection_id, mode_):
    print collection_id
    docs = get_db(mode_).read(collection_id)
    print docs
    return docs

from FlaskWebProject.steershared.shared_consts import *
from FlaskWebProject.steershared.dbconnectors import mongodb_connector, docdb_connector


def transfer_data():
    for collection_id in COLLECTIONS:
        print collection_id
        mongo_docs = mongodb_connector.read(collection_id)
        if mongo_docs:
            print 'Found mongo docs for ' + collection_id

            retailer_names = ['The Veg Box Cafe', 'Elite Beauty']

            if collection_id == RETAILERS:
                mongo_docs = [doc for doc in mongo_docs if doc[NAME] in retailer_names]
            elif collection_id == PRODUCTS:
                mongo_docs = [doc for doc in mongo_docs if doc[RETAILER_NAME] == retailer_names]

            #existing_docs = docdb_connector.read(collection_id)
            #existing_ids = [existing_doc[ID] for existing_doc in existing_docs]
            #docdb_connector.delete(existing_ids)
            #docdb_connector.create(collection_id, mongo_docs)


if __name__ == '__main__':
    transfer_data()

from FlaskWebProject import app
from FlaskWebProject.steershared.shared_consts import ID, MONGO_DB, DB_ID
from pymongo import MongoClient
from bson.objectid import ObjectId
from copy import deepcopy
from functools import wraps

# Mongo uses '_id' instead of 'id' attribute. This detail is abstracted away from clients.
# All Spot Markets docs use 'id' attribute.
_mongo_id_key = '_id'


def _get_mongo_id(id_):
    """Transforms id string in mongo id obj"""
    return ObjectId(id_)


def _extract_docs(cursor):
    docs = []
    for doc in cursor:
        doc[ID] = str(doc[_mongo_id_key])
        del doc[_mongo_id_key]
        docs.append(doc)
    return docs


def gen_connector(mode):
    return MongoConnector(mode)


def deco_retry(f):
    """Function wrapper for all MongoConnector CRUD operations. Reinstantiates db client if operation fails"""
    @wraps(f)
    def f_retry(self, *args, **kwargs):
        mtries = 2
        while mtries > 1:
            # Try to perform the operation
            try:
                return f(self, *args, **kwargs)
            # Reinstantiate db client if exception is raised
            except Exception as e:
                self.gen_client()
                print type(e)
                print e
            print 'Retrying mongodbconnector'
            mtries -= 1
        # This will execute as the final try, if this call fails then the operation will fail
        return f(self, *args, **kwargs)

    return f_retry  # true decorator


class MongoConnector:
    """Connector for MongoDB database"""
    def __init__(self, mode):
        self._mode = mode
        self._client = None
        self.gen_client()

    def gen_client(self):
        """Generates db client"""
        self._client = MongoClient(app.config[MONGO_DB])['{0}_{1}'.format(app.config[DB_ID], self._mode)]

    @deco_retry
    def create(self, collection_id, docs):
        """Creates docs, returns list of str representing ids of created docs"""
        # Recommendation Engine may pass a dictionary, so ensure it's wrapped in a list
        if type(docs) is dict:
            docs = [docs]
        try:
            results = self._client[collection_id].insert_many(docs)
            ids = [str(inserted_id) for inserted_id in results.inserted_ids]
            for doc in docs:
                del doc[_mongo_id_key]
            return ids
        except Exception as e:
            print type(e)
            print e
            raise e

    @deco_retry
    def read(self, collection_id, query_dicts=None):
        """"Reads docs, returns list of dictionaries representing docs"""
        # query_dicts are dictionaries which represent queries.
        # E.g. { NAME: 'foo' } would return all docs where NAME='foo'

        # Recommendation Engine may pass a dictionary, so ensure it's wrapped in a list
        if type(query_dicts) is dict:
            query_dicts = [query_dicts]

        try:
            # If there are no query dicts then find all docs in the collection
            if not query_dicts:
                cursor = self._client[collection_id].find()
                return _extract_docs(cursor)
            # Else find all docs that match at least one of the query dicts
            # N.B. We allow multiple query dicts so that they can search for multiple ids [{ID: 'foo'}, {ID: 'bar'}...]
            else:
                docs = []
                for query_dict in query_dicts:
                    if ID in query_dict.keys():
                        query_dict[_mongo_id_key] = ObjectId(query_dict[ID])
                        del query_dict[ID]
                    cursor = self._client[collection_id].find(query_dict)
                    docs.extend(_extract_docs(cursor))
                return docs
        except Exception as e:
            print type(e)
            print e
            raise e

    @deco_retry
    def update(self, collection_id, updated_docs):
        """Updates docs, returns list of str representing ids of updated docs"""
        # Recommendation Engine may call this function directly and pass a dictionary, so ensure it's wrapped in a list
        if type(updated_docs) is dict:
            updated_docs = [updated_docs]

        # Deepy copy because the doc has 'id' but mongo uses '_id', so attr names are going to change but we want
        # to abstract this detail away from the caller
        updated_docs = deepcopy(updated_docs)

        updated_ids = []
        for updated_doc in updated_docs:
            try:
                id_ = updated_doc[ID]
                updated_doc = {'$set': updated_doc}
                self._client[collection_id].update_one({_mongo_id_key: ObjectId(id_)}, updated_doc)
                updated_ids.append(id_)
            except Exception as e:
                print type(e)
                print e
                raise e
        return updated_ids

    @deco_retry
    def replace(self, collection_id, replace_docs):
        """Replaces docs, returns list of str representing ids of replaced docs"""
        # Recommendation Engine may pass a dictionary, so ensure it's wrapped in a list
        if type(replace_docs) is dict:
            replace_docs = [replace_docs]

        # Copy because the doc has 'id' but mongo uses '_id', so attr names are going to change but we want
        # to abstract this detail away from the caller
        replace_docs = deepcopy(replace_docs)

        replace_ids = []
        for replace_doc in replace_docs:
            try:
                id_ = replace_doc[ID]
                self._client[collection_id].replace_one({_mongo_id_key: ObjectId(id_)}, replace_doc)
                replace_ids.append(id_)
            except Exception as e:
                print type(e)
                print e
                raise e
        return replace_ids

    @deco_retry
    def delete(self, collection_id, ids=None):
        """Deletes docs, returns list of str representing ids of deleted docs"""
        # Recommendation Engine may pass a string, so ensure it's wrapped in a list
        if not ids:
            self._client[collection_id].delete_many({})
            return []
        else:
            if type(ids) is str:
                ids = [ids]
            for id_ in ids:
                try:
                    self._client[collection_id].delete_one({_mongo_id_key: ObjectId(id_)})
                except Exception as e:
                    print type(e)
                    print e
                    raise e
            return ids

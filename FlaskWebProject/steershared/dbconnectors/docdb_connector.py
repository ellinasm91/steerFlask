from FlaskWebProject import app
from FlaskWebProject.steershared.shared_consts import ID, DB_ID, DOCUMENTDB_HOST, DOCUMENTDB_MASTER_KEY
import pydocumentdb.errors as errors
import pydocumentdb.document_client as document_client


def gen_connector(mode):
    """Generates DocumentDB connector"""
    return DocdbConnector(mode)


def gen_client(self):
    """Generates db client"""
    return document_client.DocumentClient(app.config[DOCUMENTDB_HOST],
                                          {'masterKey': app.config[DOCUMENTDB_MASTER_KEY]})


class IDisposable:
    """ A context manager to automatically close an object with a close method
    in a with statement. """

    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        return self.obj  # bound to target

    def __exit__(self, exception_type, exception_val, trace):
        # extra cleanup in here
        self = None


class DocdbConnector:
    """Connector for DocumentDB database"""
    def __init__(self, mode):
        self._mode = mode

    @staticmethod
    def get_collection_link(self, id_):
        """Gets str link for a collection"""
        return 'dbs/{0}/colls/{1}'.format(app.config[DB_ID], id_)

    @staticmethod
    def get_document_link(self, collection_id, id_):
        """Gets str link for a document"""
        return self.get_collection_link(collection_id) + '/docs/{0}'.format(id_)

    def create(self, collection_id, docs):
        """Creates docs, returns list of str representing ids of created docs"""
        with IDisposable(self.gen_client()) as client:
            created_ids = []
            # Recommendation Engine may pass a dictionary, so ensure it's wrapped in a list
            if type(docs) is dict:
                docs = [docs]
            for doc in docs:
                new_doc = client.CreateDocument(self.get_collection_link(collection_id), doc)
                created_ids.append(new_doc[ID])
            return created_ids

    def read(self, collection_id, query_dicts):
        """Reads docs, returns list of dictionaries representing docs"""
        # query_dicts are dictionaries which represent queries.
        # E.g. { NAME: 'foo' } would return all docs where NAME='foo'
        with IDisposable(self.gen_client()) as client:
            docs = []
            # If there are no query dicts then find all docs in the collection
            if query_dicts is None:
                docs = client.ReadDocuments(self.get_collection_link(collection_id)).fetch_items()
            # Else find all docs that match at least one of the query dicts
            # N.B. We allow multiple query dicts so that they can search for multiple ids [{ID: 'foo'}, {ID: 'bar'}...]
            else:
                # Recommendation Engine may pass a dictionary, so ensure it's wrapped in a list
                if type(query_dicts) is dict:
                    query_dicts = [query_dicts]

                for query_dict in query_dicts:
                    try:
                        # TODO: Optimize! If the only query involves an id then use ReadDocument instead
                        doc = client.QueryDocument(self.get_collection_link(collection_id), query_dict)
                        docs.append(doc)
                    except errors.DocumentDBError as e:
                        if e.status_code == 404:
                            print('A {0} with id \'{1}\' does not exist'.format(collection_id, query_dict))
                        else:
                            raise errors.HTTPFailure(e.status_code)
        return docs

    def update(self, collection_id, new_docs):
        """Updates docs, returns list of str representing ids of updated docs"""
        with IDisposable(self.gen_client()) as client:
            # Recommendation Engine may pass a dictionary, so ensure it's wrapped in a list
            if type(new_docs) is dict:
                new_docs = [new_docs]
            updated_ids = []
            for new_doc in new_docs:
                try:
                    # DocumentDB client has no update method, so we need to read and then replace
                    existing_doc = client.ReadDocument(self.get_document_link(collection_id, new_doc[ID]))
                    existing_doc.update(new_doc)
                    client.ReplaceDocument(self.get_document_link(collection_id, existing_doc[ID]), existing_doc)
                    updated_ids.append(existing_doc[ID])
                except errors.DocumentDBError as e:
                    if e.status_code == 404:
                        print('A {0} with id \'{1}\' does not exist'.format(collection_id, new_doc[ID]))
                    else:
                        raise errors.HTTPFailure(e.status_code)
            return updated_ids

    def replace(self, collection_id, replace_docs):
        """Replaces docs, returns list of str representing ids of replaced docs"""
        with IDisposable(self.gen_client()) as client:
            # Recommendation Engine may pass a dictionary, so ensure it's wrapped in a list
            if type(replace_docs) is dict:
                replace_docs = [replace_docs]

            replace_ids = []

            for replace_doc in replace_docs:
                try:
                    client.ReplaceDocument(self.get_document_link(collection_id, replace_doc[ID]), replace_doc)
                    replace_ids.append(replace_doc[ID])
                except Exception as e:
                    print type(e)
                    print e
                    raise e
            return replace_ids

    def delete(self, collection_id, ids):
        """Deletes docs, returns list of str representing ids of deleted docs"""
        with IDisposable(self.gen_client()) as client:
            # Recommendation Engine may pass a str, so ensure it's wrapped in a list
            if type(ids) is str:
                ids = [ids]

            deleted_ids = []
            for id_ in ids:
                try:
                    client.DeleteDocument(self.get_document_link(collection_id, id_))
                    deleted_ids.append(id_)
                except errors.DocumentDBError as e:
                    if e.status_code == 404:
                        print('A {0} with id \'{1}\' does not exist'.format(collection_id, id_))
                    else:
                        raise errors.HTTPFailure(e.status_code)
        return deleted_ids

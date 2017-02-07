from FlaskWebProject import app
from FlaskWebProject.steershared.shared_consts import *
import importlib
import os


def import_db_connector_module(module_name=app.config[DB_ACCESS_MODULE]):
    """
    Imports a database connector module
    :param module_name: str is module name. Defaults to value found in app config
    """
    return importlib.import_module(module_name)


def get_db(headers):
    """
    Returns a database connector
    :param headers: Dictionary representing configuration.
    MODE_HEADER_KEY determines mode (e.g. debug, eval)
    DB_HEADER_KEY determines connector type (e.g. MongoDB, DocumentDB)
    :return: Database Connector
    """
    try:
        #mode = str(headers[MODE_HEADER_KEY])
        mode="debug"
    except (KeyError, TypeError):
        if type(headers) is unicode:
            headers = str(headers)
        # Check if it's a str because we used to have a mode (str) argument instead of headers
        mode = headers if type(headers) is str else app.config[DEFAULT_MODE]

    try:
        db_module_name = headers[DB_HEADER_KEY]
    except (KeyError, TypeError):
        db_module_name = app.config[DB_ACCESS_MODULE]

    db_module = importlib.import_module('{0}.{1}'.format(app.config[DB_PACKAGE_PATH], db_module_name))

    key = '{0}_{1}'.format(db_module_name, mode)
    if key not in _dbs.keys():
        _dbs[key] = db_module.gen_connector(mode)
    return _dbs[key]


def rename_attrs(collection_id, attr_dicts, mode):
    """
    Renames attributes in a collection
    :param collection_id: str
    :param attr_dicts: List of Dictionaries (Key is old_attr, Value is new_attr)
    :param mode: Database mode
    :return:
    """
    db = get_db(mode)
    docs = db.read(collection_id)
    for doc in docs:
        for old_attr, new_attr in attr_dicts.iteritems():
            doc[new_attr] = doc[old_attr]
            del doc[old_attr]
    db.replace(collection_id, docs)


def add_ids(docs, ids):
    """
    Adds id attributes to documents
    :param docs: List of documents
    :param ids: List of ids
    """
    zipped = zip(docs, ids)
    for doc, id_ in zipped:
        doc[ID] = id_


def denormalize_docs(referencee_collection_id, referencer_collection_id, reference_prefix, denorm_attrs, mode):
    """
    Denormalizes attributes from one collection to another
    https://en.wikipedia.org/wiki/Denormalization
    :param referencee_collection_id: Collection which is referenced
    :param referencer_collection_id: Collection which contains the reference
    :param reference_prefix: Prefix to assign to denormalized attributes in the referencer collection
    :param denorm_attrs: Attributes from referencee collection to copy to referencer collection
    :param mode: Database mode
    """
    db = get_db(mode)
    referencee_docs = db.read(referencee_collection_id)
    referencer_docs = db.read(referencer_collection_id)

    # If they only passed one attribute then wrap it in a list
    if type(denorm_attrs) is str:
        denorm_attrs = [denorm_attrs]

    print "Denormalizing from {0} to {1}".format(referencee_collection_id, referencer_collection_id)

    for referencee in referencee_docs:
        for referencer in referencer_docs:
            if referencer['{0}_{1}'.format(reference_prefix, ID)] == referencee[ID]:
                for attr in denorm_attrs:
                    referencer['{0}_{1}'.format(reference_prefix, attr)] = referencee[attr]

    db.update(referencer_collection_id, referencer_docs)


def relink_ids(referencee_collection_id, referencer_collection_id, reference_prefix, denorm_attr, mode):
    """
    Relinks reference ids if referenced collection has been reimported with a new set of ids
    N.B. This is only possible if the referencer_collection has denormalized data
    :param referencee_collection_id: Collection which is referenced
    :param referencer_collection_id: Collection which contains the references
    :param reference_prefix: Prefix to assign to denormalized attributes in the referencer collection
    :param denorm_attr: Attribute which is denormalized, so can be found in both collections and used to relink the id
    :param mode: Database mode
    """
    db = get_db(mode)
    referencer_docs = db.read(referencer_collection_id)
    for referencer in referencer_docs:
        try:
            referencee_docs = db.read(referencee_collection_id,
                                      {denorm_attr: referencer['{0}_{1}'.format(reference_prefix, denorm_attr)]})
            for referencee in referencee_docs:
                referencer['{0}_{1}'.format(reference_prefix, ID)] = referencee[ID]
        except KeyError:
            pass
    db.update(referencer_collection_id, referencer_docs)


def obfuscate_attr(collection_id, attr, mode):
    """
    Obfuscates an attribute with integer values
    :param collection_id: Name of collection
    :param attr: Attribute to obfuscate
    :param mode: Database mode
    :return:
    """
    db = get_db(mode)
    docs = db.read(collection_id)
    obf_map = {}
    for idx, doc in enumerate(docs):
        # If we have already obfuscated the value then set attr to the previous obfuscation
        if doc[attr] in obf_map.keys():
            doc[attr] = obf_map[doc[attr]]
        # Else set attr to the current index
        else:
            obf_map[doc[attr]] = idx
            doc[attr] = idx

    with open(os.path.join(os.getcwd(), '{0}_{1}_obfuscation_mapping.txt'.format(collection_id, attr)), 'w') as f:
        f.write(str(obf_map))

    db.update(collection_id, docs)


# Private variables
_dbs = {}

if __name__ == '__main__':
    obfuscate_attr(CONSUMERS, EMAIL, EVAL)

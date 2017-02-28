from FlaskWebProject.steershared.shared_consts import *
from FlaskWebProject.steershared.dbconnectors.db_helpers import get_db
import os
import json
from bson import json_util
from bson.objectid import ObjectId

def get_dir_name(db_access_module, mode):
    return '{0}_{1}'.format(db_access_module, mode)


def import_db(db_access_module, mode, path=os.getcwd()):
    dir_name = '{0}_{1}'.format(db_access_module, mode)
    dir_path = os.path.join(path, dir_name)

    db = get_db({DB_HEADER_KEY: db_access_module, MODE_HEADER_KEY: mode})

    for coll in COLLECTIONS:
        file_path = os.path.join(dir_path, '{0}.txt'.format(coll))
        with open(file_path.format(coll), 'r') as f:
            docs = json.load(f)

# Why delete the input ID?
            for doc in docs:
                doc[ID] = ObjectId(doc[ID])
                doc[objectID] = doc[ID]
                del doc[ID]
        db.delete(coll)
        if(docs):
            print 'Importing {0}.txt'.format(coll)
            db.create(coll, docs)
        else:
            print 'Empty file {0}.txt'.format(coll)


def export_db(db_access_module, mode, path=os.getcwd()):
    dir_name = get_dir_name(db_access_module, mode)
    dir_path = os.path.join(path, dir_name)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    db = get_db({DB_HEADER_KEY: db_access_module, MODE_HEADER_KEY: mode})

    for coll in COLLECTIONS:
        docs = db.read(coll)
        file_path = os.path.join(dir_path, '{0}.txt'.format(coll))
        with open(file_path.format(coll), 'w') as f:
            json.dump(docs, f, default=json_util.default)


if __name__ == '__main__':
    import_db('mongodb_connector', EVAL)

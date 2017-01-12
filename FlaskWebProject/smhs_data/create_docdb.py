from FlaskWebProject.steershared.dbconnectors.docdb_connector import IDisposable, gen_client
from FlaskWebProject.steershared.shared_consts import *
import FlaskWebProject.steerapi.data_helpers
import pydocumentdb.errors as errors
from time import sleep
from FlaskWebProject import app


def create_db(db_id, collections):
    with IDisposable(gen_client()) as client:
        try:
            print("Creating Database")
            client.CreateDatabase({"id": db_id})
            print('Database with id \'{0}\' created'.format(db_id))
        except errors.DocumentDBError as e:
            if e.status_code == 409:
                print('A database with id \'{0}\' already exists'.format(db_id))
            else:
                raise errors.HTTPFailure(e.status_code)

        print("Creating Collections")
        for collection in collections:
            print("Creating " + collection)
            try:
                client.CreateCollection(FlaskWebProject.steerapi.data_helpers.get_db_link(db_id), {"id": collection})
                print('Collection with id \'{0}\' created'.format(collection))

            except errors.DocumentDBError as e:
                if e.status_code == 409:
                    print('A collection with id \'{0}\' already exists'.format(collection))
                else:
                    raise errors.HTTPFailure(e.status_code)
            sleep(10)


if __name__ == '__main__':
    dbs = [DEBUG]
    for db in dbs:
        create_db('{0}_{1}'.format(app.config[DB_ID], db), COLLECTIONS)

from FlaskWebProject.steershared.dbconnectors.db_helpers import get_db
from FlaskWebProject.steershared.shared_consts import *
from time import time


def test(num_docs):
    doc = {IS_FILE_UPLOAD: False, NAME: 'Playstation 4', PRICE: 285.4, QUANTITY: 10,
           RETAILER_ID: '57c843145c92eb476191d6d9'}
    docs = []
    for i in range(num_docs):
        docs.append(doc)

    db = get_db(DEBUG)
    db.delete(BEACONS)

    t0 = time()
    ids = db.create(BEACONS, docs)
    t1 = time() - t0
    print('Create {0}: {1}'.format(num_docs, t1))

    read_ids = {ID: id_ for id_ in ids}

    t0 = time()
    docs = db.read(BEACONS, read_ids)
    t1 = time() - t0
    print('Read {0}: {1}'.format(num_docs, t1))

    for doc in docs:
        doc[NAME] = 'Xbox One'

    t0 = time()
    ids = db.update(BEACONS, docs)
    t1 = time() - t0
    print('Update {0}: {1}'.format(num_docs, t1))

    t0 = time()
    db.delete(BEACONS, ids)
    t1 = time() - t0
    print('Delete {0}: {1}'.format(num_docs, t1))


if __name__ == '__main__':
    counts = [1, 2]
    for count in counts:
        test(count)

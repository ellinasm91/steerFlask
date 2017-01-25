# -*- coding: utf-8 -*-
from db_helpers import get_db
from FlaskWebProject.steershared.shared_consts import *
import re


def attr_to_str(collection_id, headers, attr):
    db = get_db(headers)
    docs = db.read(collection_id)
    for doc in docs:
        if attr in doc.keys():
            doc[attr] = str(doc[attr])
    db.update(collection_id, docs)


def str_to_float(mode, collection_id, attr):
    db = get_db(mode)
    docs = db.read(collection_id)

    print docs

    for doc in docs:
        is_dollar = u'$' in doc[attr]

        # replace(u'£', u'')
        doc[attr] = doc[attr].replace(u'\xa33', u'').replace(u'\xa30', u'').replace('n/a', '-1').replace(',', '').\
            replace('From ', '').replace('From: ', '').replace(' / 15 sachets', '').replace('from just ', '').\
            replace('from ', '').replace(u'USD $', '').replace(u'$', '')

        doc[attr] = doc[attr].strip()

        if not doc[attr]:
            doc[attr] = '-1'

        full_hyphen_pattern = '[0-9]+-[0-9]+'
        half_hyphen_pattern = '[0-9]+-'
        print doc[attr]
        if re.match(full_hyphen_pattern, doc[attr]):
            try:
                half_match = re.match(half_hyphen_pattern, doc[attr])
                doc[attr] = re.sub(full_hyphen_pattern, half_match.group(0), doc[attr]).replace('-', '')
            except Exception as e:
                print e
                print doc[attr]
                raise e
        try:
            doc[attr] = float(doc[attr])
            if is_dollar:
                doc[attr] *= 0.76
        except Exception as e:
            print e
            print doc
            print doc[attr]
            raise e

    print docs

    db.update(collection_id, docs)


if __name__ == '__main__':
    attr_to_str(CONSUMERS, DEBUG, 'date')

import csv

import upload_helpers
from FlaskWebProject.steerapi import crud_safety
from FlaskWebProject.steershared.dbconnectors.db_helpers import get_db
from FlaskWebProject.steershared.shared_consts import *


def upload(mode):
    headers = upload_helpers.get_dev_headers(mode)
    crud_safety.delete(IAB_CATEGORIES, headers, {})
    # Savvas: name of the file used to add the categories in the DB
    filename = "categories.csv"
    # Savvas: category IDs
    prefix = "IAB"
    parent_num = 0
    child_num = 0
    categories = []
    current_parent_name = ''
    # Savvas: Read each category from the csv file and add generate the correct ID
    with open(filename, 'rb') as csvfile:
        data = csv.reader(csvfile)
        # Savvas: Read file row by row
        for row in data:
            if row[0]:
                parent_num += 1
                child_num = 0
                # Savvas: Generate only categort Id and add to the DB
                category_code = prefix + str(parent_num)
                category_name = row[0]
                current_parent_name = category_name
                categories.append({CATEGORY_CODE: category_code, NAME: category_name})
            else:
                child_num += 1
                # Savvas: Generate parent Id and category Id
                parent_code = prefix + str(parent_num)
                category_code = parent_code + '-' + str(child_num)
                category_name = row[1]
                categories.append({CATEGORY_CODE: category_code, NAME: category_name,
                                   PARENT_CATEGORY_CODE: parent_code, PARENT_NAME: current_parent_name})
    print categories

    crud_safety.create(IAB_CATEGORIES, headers, categories)
    categories = crud_safety.read(IAB_CATEGORIES, headers, None)

    child_categories = []
    parent_categories = []

    for category in categories:
        if PARENT_CATEGORY_CODE in category.keys():
            child_categories.append(category)
        else:
            parent_categories.append(category)

    for child_category in child_categories:
        for parent_category in parent_categories:
            if child_category[PARENT_CATEGORY_CODE] == parent_category[CATEGORY_CODE]:
                child_category[PARENT_ID] = parent_category[ID]

    crud_safety.update(IAB_CATEGORIES, headers, categories)

if __name__ == '__main__':
    mode_ = EVAL
    #upload(mode_)
    headers_ = upload_helpers.get_dev_headers(mode_)
    print 'CATS'
    print crud_safety.read(IAB_CATEGORIES, headers_, None)
    db_ = get_db(mode_)
    print db_.read(IAB_CATEGORIES)
    print crud_safety.read_bypass(IAB_CATEGORIES, mode_)
    print ''

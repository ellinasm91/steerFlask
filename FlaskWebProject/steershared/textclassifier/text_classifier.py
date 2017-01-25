from FlaskWebProject import app
from aylienapiclient import textapi
from time import sleep
from FlaskWebProject.steershared.shared_consts import ID, TEXT_API_APP_ID, TEXT_API_KEY, TEXT, TAXONOMY, IAB_QAG, \
                                                        CATEGORIES, CONFIDENT, SCORE


# Savvas: Get the categories using AYLIEN API and return the most relevant
#         if there is one.
def get_category(input_text):
    c = textapi.Client(app.config[TEXT_API_APP_ID], app.config[TEXT_API_KEY])
    sleep(1)
    # Savvas: Send the test the text Classifier. It's classifying by taxonomy.
    s = c.ClassifyByTaxonomy({TEXT: input_text, TAXONOMY: IAB_QAG})
    result = None
    score_level = 0.10
    # Savvas: Returns None if there is no relevant,trusted category.
    for category in s[CATEGORIES]:
        if category[CONFIDENT]:
            if category[SCORE] > score_level:
                result = category[ID]
                score_level = category[SCORE]
            else:
                pass
        else:
            pass
    return result

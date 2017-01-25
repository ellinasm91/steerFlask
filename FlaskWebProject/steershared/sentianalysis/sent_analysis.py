from FlaskWebProject import app
import urllib2
import urllib
import base64
import json
from FlaskWebProject.steershared.shared_consts import SENT_API_KEY, ACCOUNT_KEY, AUTHORIZATION, \
                                                        CONTENT_TYPE, TEXT, SENT_SCORE, KEY_PHRASES


# Savvas: Sentiment analysis by Azure's API. Takes text and returns a sentiment
#         score from 1-5. Really bad to really good.
def get_sentiment(input_text):
    credentials = base64.b64encode(ACCOUNT_KEY + app.config[SENT_API_KEY])
    headers = {CONTENT_TYPE: 'application/json', AUTHORIZATION: ('Basic ' + credentials)}
    params = {TEXT: input_text}

    # Savvas: Request score by text
    sentiment_url = ('https://api.datamarket.azure.com/data.ashx/amla/text-analytics/v1/GetSentiment?'\
                     + urllib.urlencode(params))
    req = urllib2.Request(sentiment_url, None, headers)
    response = urllib2.urlopen(req)
    result = response.read()
    obj = json.loads(result)
    # Savvas: Score received from 0.0-1.0
    score_level = obj[SENT_SCORE]

    # Savvas: Receive key phrases in text. This is not used because it is not needed.
    #         The text Classifier works better with whole sentences instead of just key phrase
    #key_phrases_url = ('https://api.datamarket.azure.com/data.ashx/amla/text-analytics/v1/GetKeyPhrases?' +
                        #urllib.urlencode(params))
    #req = urllib2.Request(key_phrases_url, None, headers)
    #response = urllib2.urlopen(req)
    #result = response.read()
    #obj = json.loads(result)
    #key_phrases = str(','.join(obj[KEY_PHRASES]))

    # Savvas: Returns polarity to know whether we increase a category in the consumer profile
    #         or decrease it. Because the text will be classified after the sentiment analysis.
    return score_level

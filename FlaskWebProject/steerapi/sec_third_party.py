from FlaskWebProject import app
import urllib2
import json
import requests
from requests_oauthlib import OAuth1
import urllib
from FlaskWebProject.steershared.shared_consts import ACCESS_TOKEN, ID, SECRET_TOKEN, THIRD_PARTY_NAME, TWITTER_KEY, \
    TWITTER_SECRET, FACEBOOK, GOOGLE_PLUS, PINTEREST, TWITTER, DATA


def get_tw_oauth(consumer_key, consumer_secret):
    oauth = OAuth1(app.config[TWITTER_KEY], client_secret=app.config[TWITTER_SECRET], resource_owner_key=consumer_key,
                   resource_owner_secret=consumer_secret)
    return oauth


def get_third_party_user_id_from_token(in_data):
    access_token = in_data[ACCESS_TOKEN]
    refresh_token = in_data[SECRET_TOKEN]
    third_party_name = in_data[THIRD_PARTY_NAME]

    try:
        if third_party_name == FACEBOOK:
            result = urllib2.urlopen("https://graph.facebook.com/me?access_token=" + access_token).read()
            identity = json.loads(result)[ID]
        elif third_party_name == GOOGLE_PLUS:
            result = urllib.urlopen("https://www.googleapis.com/plus/v1/people/me?access_token=" + access_token).read()
            identity = json.loads(result)[ID]
        elif third_party_name == TWITTER:
            tw_oauth = get_tw_oauth(access_token, refresh_token)
            result = requests.get(url="https://api.twitter.com/1.1/account/verify_credentials.json", auth=tw_oauth)
            identity = result.json()[ID]
        elif third_party_name == PINTEREST:
            result = urllib2.urlopen("https://api.pinterest.com/v1/me?access_token=" + access_token).read()
            identity = json.loads(result)[DATA][ID]
        else:
            identity = None
        return identity
    except Exception, e:
        print e
        return None

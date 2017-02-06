class Cfg(object):
    DEBUG = False
    TESTING = False
    REST_URI = 'http://steerflaskapp.azurewebsites.net'
    JWT_SECRET = 'toomanysecrets'
    JWT_ALGO = 'HS256'
    DB_ID = 'steerdb'
    DEFAULT_MODE = 'debug'
    DOCUMENTDB_HOST = 'https://steerdatabase.documents.azure.com:443/'
    DOCUMENTDB_MASTER_KEY = 'fJxIpPAIXXZzoArleTZhlrumtoF50ug8ztRcXS6J2e2hUu2WLkPZys9IAwDKVtuyE0XwyQ6cXtTvzh83gt2N3A=='
    MONGO_USER = 'SpotMarketAdmin'
    MONGO_PASS = 'NwDqsk9kO6dl'
    MONGO_HOST = 'mongodb://13.74.153.149' # DNS Servers got DDOSed so DNS stopped working and we changed to IP,
                                            # We left it like this just in case it happens again
    #MONGO_HOST = 'mongodb://vps301173.ovh.net'
    MONGO_DB = '{0}/{1}'.format(MONGO_HOST, DB_ID)
    DB_PACKAGE_PATH = 'FlaskWebProject.steershared.dbconnectors'
    DB_ACCESS_MODULE = 'mongodb_connector'
    TEXT_API_APP_ID = 'c9b4861d'
    TEXT_API_KEY = 'c45db1fa44f0ce2e4ba2a9da72cb14da'
    SENT_API_KEY = 'sAbv//CA0RYDi9408NlqZQVSQqIehrInFniC+EThc6M'
    TWITTER_KEY = 'OYNZ2IkPsIngHYGDXisSWloaQ'
    TWITTER_SECRET = '3ZFmqrpmBJaarNK6YhhrCJaXXEVCNtx1zfPGY9t9gJfePokjVS'


class ProductionCfg(Cfg):
    DEBUG = False


class ProductionCfg(Cfg):
    DEBUG = False


class ProductionCfg(Cfg):
    TESTING = True
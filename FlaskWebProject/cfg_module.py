class Cfg(object):
    DEBUG = True
    TESTING = False
    #REST_URI = 'http://localhost:5555'
    REST_URI = 'https://steerflaskapp.azurewebsites.net'
    JWT_SECRET = 'toomanysecrets'
    JWT_ALGO = 'HS256'
    DB_ID = 'spotmarket'
    DEFAULT_MODE = 'debug'
   
    #DOCUMENTDB_HOST = 'https://steerdatabase.documents.azure.com:443/'
    #DOCUMENTDB_MASTER_KEY = 'fJxIpPAIXXZzoArleTZhlrumtoF50ug8ztRcXS6J2e2hUu2WLkPZys9IAwDKVtuyE0XwyQ6cXtTvzh83gt2N3A=='
    #MONGO_USER = 'admin'
    MONGO_USER = 'SpotMarketAdmin'
    #MONGO_PASS = 'kingkong'
    MONGO_PASS = 'NwDqsk9kO6dl'
    #MONGO_HOST = 'mongodb://127.0.0.1/'
    MONGO_HOST = 'mongodb://13.74.28.28' # DNS Servers got DDOSed so DNS stopped working and we changed to IP,
                                            # We left it like this just in case it happens again
    """
    DOCUMENTDB_HOST = 'https://steerdatabase.documents.azure.com:443/'
    DOCUMENTDB_MASTER_KEY = 'fJxIpPAIXXZzoArleTZhlrumtoF50ug8ztRcXS6J2e2hUu2WLkPZys9IAwDKVtuyE0XwyQ6cXtTvzh83gt2N3A=='
    #MONGO_USER = 'SpotMarketAdmin'
    #MONGO_PASS = 'NwDqsk9kO6dl'
    #MONGO_HOST = 'mongodb://13.74.28.28' # DNS Servers got DDOSed so DNS stopped working and we changed to IP,
                                            # We left it like this just in case it happens again
    MONGO_USER = 'myUserAdmin'
    MONGO_PASS = 'abc123'
    MONGO_HOST = 'mongodb://localhost' # DNS Servers got DDOSed so DNS stopped working and we changed to IP,
    #MONGO_HOST = 'mongodb://vps301173.ovh.net'
    """
    MONGO_DB = '{0}/{1}'.format(MONGO_HOST, DB_ID)
    DB_PACKAGE_PATH = 'FlaskWebProject.steershared.dbconnectors'
    DB_ACCESS_MODULE = 'mongodb_connector'
    AZURE_ACCOUNT_NAME = 'spotmarketdatastorage'
    AZURE_ACCOUNT_KEY ='yj7j6UO3Ult1YpW/ZiXeDOdevF8iMOghhCZRjoGkHXt6rwyIaQ6CmQclWu2vskDE3vhwTu98ypS/7NFBAa5ddg=='
    TEXT_API_APP_ID = 'c9b4861d'
    TEXT_API_KEY = 'c45db1fa44f0ce2e4ba2a9da72cb14da'
    SENT_API_KEY = 'sAbv//CA0RYDi9408NlqZQVSQqIehrInFniC+EThc6M'
    TWITTER_KEY = 'OYNZ2IkPsIngHYGDXisSWloaQ'
    TWITTER_SECRET = '3ZFmqrpmBJaarNK6YhhrCJaXXEVCNtx1zfPGY9t9gJfePokjVS'


class ProductionCfg(Cfg):
    DEBUG = True


class ProductionCfg(Cfg):
    DEBUG = False


class ProductionCfg(Cfg):
    TESTING = False

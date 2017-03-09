from abstractconnector import AbstractConnector
from FlaskWebProject.steershared.shared_consts import *
from azure.storage.blob import ContentSettings, BlockBlobService, PublicAccess, BlobPermissions
from azure.storage import AccessPolicy
from FlaskWebProject.steershared.shared_consts import AZURE_ACCOUNT_NAME, AZURE_ACCOUNT_KEY, CONTAINER, SERIES_COLUMN, \
    ID
from collections import OrderedDict
import datetime
class AzureBlobConnector(AbstractConnector):
    """Connector for Azure Blob Storage. 
    To maintain conceptual consistency with our other connectors, each 
    AzureBlobConnector instance connects to a single container. A blob 
    is analogous to a database table and a container is analogous to 
    the database itself.
    """
    def __init__(self, config, tables):
        """
        config (Dict): Configuration for connecting to Azure Blob Storage
        tables (AttrDict): Names of blobs
        """
        super(AzureBlobConnector, self).__init__(config, tables)
        self._service=BlockBlobService(account_name=config[AZURE_ACCOUNT_NAME], account_key=config[AZURE_ACCOUNT_KEY])
        # Create the container which this instance connects to
       
        self._service.create_container(config[CONTAINER], public_access=PublicAccess.Container)

    def upload_blob(self,dict): #upload it now!
    
        self._service.create_blob_from_bytes(dict[CONTAINER],dict[BLOBNAME],dict[IMAGE_URL], content_settings=ContentSettings(content_type='image/jpeg'))
        today = datetime.datetime.utcnow()
        todayTyear = today + datetime.timedelta(weeks=48)
        url = self._service.generate_blob_shared_access_signature(dict[CONTAINER], dict[BLOBNAME], BlobPermissions.READ, todayTyear, today) #get the shared access signature!
        url = self._service.make_blob_url(dict[CONTAINER],dict[BLOBNAME],"http", url)
        return url
  
    def __str__(self):
        return 'AzureBlobConnector'
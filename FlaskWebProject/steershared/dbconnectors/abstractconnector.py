from abc import ABCMeta, abstractmethod


class AbstractConnector():
    """Abstract base class for data connectors"""
    __metaclass__ = ABCMeta
    def __init__(self, config, tables):
        """
        config (Dict): Configuration for connecting to connected storage
        tables (AttrDict): Names of tables
        """
        self._config = config
        self.tables = tables

    @abstractmethod
    def upload_blob(self,dict):
        """
        upload images
        """
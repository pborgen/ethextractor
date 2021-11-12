import os
from ethextractor.environment.yamlReader import YamlReader
from ethextractor.environment.environment_reader import EnvironmentReader

class Properties:
    _instance = None
    _yamlConfigurationFile = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Properties, cls).__new__(cls)

        cls._yamlConfigurationFile = YamlReader().read(EnvironmentReader().getHomeDirectory() + "/ethextractor.yaml");

        return cls._instance

    def getWeb3Providerurl(self) -> str:
        cls = self.__class__
        
        return cls._yamlConfigurationFile['web3url']
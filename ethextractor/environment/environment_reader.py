import os

class EnvironmentReader:

    def getHomeDirectory(self) -> str :
        environment_variable_name = 'ETHEXTRACTOR'
        home_dir = ''

        if os.environ.get(environment_variable_name) is not None:
            home_dir = os.environ.get(environment_variable_name)
        else:
            raise Exception('environment variable ETHEXTRACTOR is not defined')
        
        return home_dir
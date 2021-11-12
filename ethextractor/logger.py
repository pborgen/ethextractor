import logging
import os

class Logger:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print('Creating the object')
            cls._instance = super(Logger, cls).__new__(cls)
            
            # Put any initialization here.
            logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

        return cls._instance
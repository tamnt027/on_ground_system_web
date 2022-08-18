import logging
from logging.handlers import RotatingFileHandler
from cachetools import TTLCache, cached

log_format = '%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(message)s'

LOG_WRITE_TO_FILE = False


if LOG_WRITE_TO_FILE == True:
    LOG_FILE_NAME = 'app_log.log'
    logging.basicConfig(filename=LOG_FILE_NAME, filemode='w',level=logging.INFO, format=log_format)

    my_handler = RotatingFileHandler(LOG_FILE_NAME, mode='w', maxBytes=64*1024*1024, 
                                    backupCount=2, encoding=None, delay=0)
    my_handler.setFormatter(log_format)
    my_handler.setLevel(logging.INFO)
    app_log = logging.getLogger('root')
    app_log.setLevel(logging.INFO)
    app_log.addHandler(my_handler)

else:
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    

@cached(cache=TTLCache(maxsize=2, ttl=60))
def logging_debug_once(message):
    logging.debug(message)

import logging
from functools import wraps


logger = logging.getLogger('lambda')
logger.setLevel(logging.INFO)

    
def log(func):

    @wraps(func)
    def wrapped_function(*args, **kwargs):
        logger.info('Recieved: args={} kwargs={}'.format(args, kwargs))
        
        result = func(*args, **kwargs)

        logger.info('Returning: {}'.format(result))

        return result
    
    return wrapped_function
    
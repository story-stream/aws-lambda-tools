import logging
from functools import wraps

logger = logging.getLogger('lambda')
logger.setLevel(logging.INFO)


def logging(func):

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        logger.info('Recieved: args={} kwargs={}'.format(args, kwargs))
        
        result = func(logger=logger, *args, **kwargs)

        logger.info('Returning: {}'.format(result))

        return result
    
    return wrapped_func
    
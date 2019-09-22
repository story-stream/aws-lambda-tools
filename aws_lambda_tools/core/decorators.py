from functools import wraps

from aws_lambda_tools.core.logger import logger


def log(func):
    
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        logger.info('Recieved: args={} kwargs={}'.format(args, kwargs))
        
        try:
            result = func(*args, **kwargs)
        except Exception:
            logger.exception('Error occurred')
            raise

        logger.info('Returning: {}'.format(result))

        return result
    
    return wrapped_function

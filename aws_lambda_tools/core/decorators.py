from functools import wraps

from aws_lambda_tools.core.logger import logger


def log(func):

    @log_after
    @log_before
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        return _execute(func, *args, **kwargs)

    return wrapped_function


def log_before(func):

    @wraps(func)
    def wrapped_function(*args, **kwargs):
        logger.info('Recieved: args={} kwargs={}'.format(args, kwargs))

        return _execute(func, *args, **kwargs)

    return wrapped_function


def log_after(func):

    @wraps(func)
    def wrapped_function(*args, **kwargs):
        result = _execute(func, *args, **kwargs)

        logger.info('Returning: {}'.format(result))

        return result

    return wrapped_function


def _execute(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception:
        logger.exception('Error occurred')
        raise
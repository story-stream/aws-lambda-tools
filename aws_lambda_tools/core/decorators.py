from collections import namedtuple
from functools import wraps


from aws_lambda_tools.core.logging import logger
from aws_lambda_tools.core.utils import execute, execute_next, log_result, merge


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


Pipeline = namedtuple(
    'PipelineConfig', 
    ['tasks', 'success', 'error', 'key'], 
    defaults=[None, None, None]
)


def pipeline(config):

    def decorator(func):
    
        @wraps(func)
        def wrapped_function(event, context):
            try:
                result = func(event, context)

                merge(event, result, config=config)

                log_result(event, result, config=config)
                
                execute_next(config.tasks, event, config=config)

            except Exception as e:
                log_result(event, result, config=config)
                
                execute(config.error, event, config=config, message=e.message)
            
            return event
        
        return wrapped_function

    return decorator
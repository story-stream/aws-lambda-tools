import json
from functools import wraps

from aws_lambda_tools.core import masks
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
        logger.info('Recieved: args={} kwargs={}'.format(json.dumps(args), json.dumps(kwargs)))

        return _execute(func, *args, **kwargs)

    return wrapped_function


def log_after(func):

    @wraps(func)
    def wrapped_function(*args, **kwargs):
        result = _execute(func, *args, **kwargs)

        logger.info('Returning: {}'.format(json.dumps(result)))

        return result

    return wrapped_function


def api(func):

    @wraps(func)
    def wrapped_function(event, context):
        try:
            event['body'] = json.loads(event.get('body', {}))
        except (ValueError, TypeError):
            # GETs do not have a body
            pass

        try:
            result = func(event, context)
        except (ValueError, TypeError):
            return {
                'statusCode': 400,
                'isBase64Encoded': False,
                'headers': {},
                'body': '',
            }

        status_code = 200
        is_encoded = False
        headers = {'Content-Type': 'application/json'}
        body = ''

        if isinstance(result, dict):
            status_code = result.get('statusCode', status_code)
            is_encoded = result.get('isBase64Encoded', is_encoded)
            headers = result.get('headers', headers)
            body = result.get('body', '')

        else:
            try:
                body, status_code, headers = result
            except ValueError:
                headers = {}
                try:
                    body, status_code = result
                except ValueError:
                    status_code = 200
                    body = result

        return {
            'statusCode': status_code,
            'isBase64Encoded': is_encoded,
            'headers': _lower_case_x_fields(headers),
            'body': json.dumps(body),
        }

    return wrapped_function


def masked_log(masked_fields=None):

    def actual_log(func):

        @masked_log_after(masked_fields=masked_fields)
        @masked_log_before(masked_fields=masked_fields)
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            return _execute(func, *args, **kwargs)

        return wrapped_function

    return actual_log


def masked_log_before(masked_fields=None):

    def actual_log_before(func):

        @wraps(func)
        def wrapped_function(*args, **kwargs):
            logged_args, logged_kwargs = masks._input(masked_fields=masked_fields, *args, **kwargs)

            logger.info('Recieved: args={} kwargs={}'.format(
                    json.dumps(logged_args),
                    json.dumps(logged_kwargs)
                )
            )

            return _execute(func, *args, **kwargs)

        return wrapped_function

    return actual_log_before


def masked_log_after(masked_fields=None):

    def actual_log_after(func):

        @wraps(func)
        def wrapped_function(*args, **kwargs):
            result = _execute(func, *args, **kwargs)

            logged_result = masks._output(result, masked_fields=masked_fields)

            logger.info('Returning: {}'.format(json.dumps(logged_result)))

            return result

        return wrapped_function

    return actual_log_after


def _execute(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception:
        logger.exception('Error occurred')
        raise

def _lower_case_x_fields(headers):
    for field, value in headers.items():
        if field.lower().startswith('x-'):
            headers[field.lower()] = headers.pop(field)
    
    return headers

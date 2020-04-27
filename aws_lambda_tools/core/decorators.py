import json
from functools import wraps
from http.client import responses

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
        event['body'] = json.loads(event['body'])
        try:
            result = func(event, context)
        except (ValueError, TypeError):
            return {
                'statusCode': 400,
                'statusDescription': responses[400],
                'isBase64Encoded': False,
                'headers': {},
                'body': '',
            }

        status_code = 200
        is_encoded = False
        headers = {'Content-Type": "application/json'}
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
            'statusDescription': responses[status_code],
            'isBase64Encoded': is_encoded,
            'headers': headers,
            'body': json.dumps(body),
        }

    return wrapped_function


def _execute(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception:
        logger.exception('Error occurred')
        raise
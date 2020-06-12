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
        logger.info('Recieved: args={} kwargs={}'.format(args, kwargs))

        return _execute(func, *args, **kwargs)

    return wrapped_function


def log_after(func):

    @wraps(func)
    def wrapped_function(*args, **kwargs):
        result = _execute(func, *args, **kwargs)

        logger.info('Returning: {}'.format(json.dumps(result)))

        return result

    return wrapped_function


def masked_log(masked_fields=None):

    def actual_log(func):

        @masked_log_after(masked_fields=masked_fields)
        @log_before
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            return _execute(func, *args, **kwargs)

        return wrapped_function

    return actual_log


def masked_log_after(masked_fields=None):

    def actual_log_after(func):

        @wraps(func)
        def wrapped_function(*args, **kwargs):
            result = _execute(func, *args, **kwargs)

            logged_result = _mask_output(result, masked_fields=masked_fields)

            logger.info('Returning: {}'.format(json.dumps(logged_result)))

            return result

        return wrapped_function

    return actual_log_after


def alb(func):

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
                'statusDescription': responses[400],
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
            'statusDescription': responses[status_code],
            'isBase64Encoded': is_encoded,
            'headers': headers,
            'body': json.dumps(body),
        }

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


def _apply_mask_to_entry(entry, masked_fields=None):
    return {
        key: _apply_mask_to_value(value, key=key, masked_fields=masked_fields)
        for key, value in entry.items()
    }


def _apply_mask_to_value(value, key=None, masked_fields=None):
    if key not in masked_fields:
        return value

    return '*' * 16


def _mask_output(result, masked_fields=None):
    if not masked_fields:
        return result

    result_body = json.loads(result['body'])

    if isinstance(result, dict):
        # Single entry in output
        masked_result = _apply_mask_to_entry(result_body, masked_fields=masked_fields)
    else:
        # Multiple entries in output
        masked_result = [
            _apply_mask_to_entry(entry, masked_fields=masked_fields)
            for entry in result_body
        ]

    result['body'] = masked_result
    return result

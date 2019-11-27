import os

from pydoc import locate


environment = os.environ.get('STYSTM_ENVIRON', 'dev')


Client = locate('aws_lambda_tools.clients.{}.Client'.format(environment))

if not Client:
    raise ImportError

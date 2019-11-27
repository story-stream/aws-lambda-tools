import os

from pydoc import locate


environment = os.environ.get('STYSTM_ENVIRON', 'dev')

client_string = 'aws_lambda_tools.clients.{}.Client'.format(environment)

Client = locate(client_string)

if not Client:
    raise ImportError('Environment {} is not valid. {}'.format(environment, client_string))

import os

from pydoc import locate


environment = os.environ.get('STYSTM_ENVIRON', 'dev')


Client = locate(f'aws_lambda_tools.clients.{environment}.Client')

if not Client:
    raise ImportError

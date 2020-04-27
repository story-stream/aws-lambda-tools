import os


environment = os.environ.get('STYSTM_ENVIRON', 'dev')

is_live = environment == 'live'

if is_live:
    from aws_lambda_tools.clients.live import Client
else:
    from aws_lambda_tools.clients.dev import Client

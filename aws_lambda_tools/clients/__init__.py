import os

try:
    is_dev = os.environ['STYSTM_ENVIRON'] == 'dev'
except KeyError:
    is_dev = False

if is_dev:
    from clients.dev_client import Client
else:
    from clients.live_client import Client

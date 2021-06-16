import os

environment = os.environ.get('STYSTM_ENVIRON', 'dev')

is_live = environment == 'live'

if is_live:
    from .live_client import Client
else:
    from .dev_client import Client
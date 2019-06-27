import os

try:
    is_dev = os.environ['STYSTM_ENVIRON'] == 'dev'
except KeyError:
    is_dev = False

if is_dev:
    try:
        # Python 2
        from dev_client import Client
    except ImportError:
        # Python 3
        from clients.dev_client import Client
else:
    try:
        #  Python 2
        from live_client import Client
    except ImportError:
        # Python 3
        from clients.live_client import Client

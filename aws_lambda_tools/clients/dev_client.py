import os
import requests
from pydoc import locate

from aws_lambda_tools import utils


class Client(object):

    def __init__(self, *args, **kwargs):
        pass

    def invoke(self, FunctionName, Payload, InvocationType='RequestResponse'):
        FunctionName = self._parse_function_name(FunctionName)

        return requests.post(
            u'http://{}'.format(FunctionName),
            json=Payload
        ).json()

    def start_execution(self, stateMachineArn, name, input, **kwargs):
        FunctionName = self._parse_function_name(FunctionName)

        f = utils.get_state_machine_name(stateMachineArn)
        return requests.post(
            u'http://{}'.format(f),
            json=input
        ).json()
    
    def _parse_function_name(self, FunctionName):
        config_location = os.environ.get('APP_CONFIG')
        if config_location:
            config = locate(config_location)
            if config and FunctionName.startswith(config.MODULE_NAME):
                FunctionName = f'{MODULE_NAME}/FunctionName[len(FunctionName):]'

        return FunctionName

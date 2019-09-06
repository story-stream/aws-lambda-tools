import os
import requests
from pydoc import locate

from aws_lambda_tools import utils


class Client(object):

    def __init__(self, *args, **kwargs):
        pass

    def invoke(self, FunctionName, Payload, InvocationType='RequestResponse'):
        FunctionName = self._parse_function_name(FunctionName)

        print(FunctionName)

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
        try:
            app = os.environ['STORYSTREAM_APP']
            if FunctionName.startswith(app):
                route = FunctionName[len(app) + 1:]
                return f'{app}/{route}'
        except KeyError:
            pass
        return FunctionName        

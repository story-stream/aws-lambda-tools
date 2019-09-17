import os
import requests

from aws_lambda_tools.core import utils


class Client(object):

    def __init__(self, *args, **kwargs):
        pass

    def invoke(self, FunctionName, Payload, InvocationType='RequestResponse'):
        ServicePath = self._parse_function_name(FunctionName)

        response = requests.post(
            u'http://{}'.format(ServicePath),
            json=Payload
        )

        # If the service does not have the path provided, call the function itself
        if response.status_code == 404:
            response = requests.post(
                u'http://{}'.format(FunctionName),
                json=Payload
            )

        return response.json()

    def start_execution(self, stateMachineArn, name, input, **kwargs):
        state_machine_name = utils.get_state_machine_name(stateMachineArn)

        ServicePath = self._parse_function_name(state_machine_name)

        response = requests.post(
            u'http://{}'.format(ServicePath),
            json=input
        )

        # If the service does not have the path provided, call the function itself
        if response.status_code == 404:
            response = requests.post(
                u'http://{}'.format(state_machine_name),
                json=input
            )

        return response.json()
    
    def _parse_function_name(self, FunctionName):
        try:
            available_services = os.environ['STORYSTREAM_SERVICES']
        except KeyError:
            return FunctionName
        
        for service in available_services.split(','):
            if FunctionName.startswith(service):
                route = FunctionName[len(service) + 1:]

                return f'{service}/{route}'       

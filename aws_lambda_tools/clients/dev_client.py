import requests
from aws_lambda_tools import utils


class Client(object):

    def __init__(self, *args, **kwargs):
        pass

    def invoke(self, FunctionName, Payload, InvocationType='RequestResponse'):
        return requests.post(
            u'http://{}'.format(FunctionName),
            json=Payload
        ).json()

    def start_execution(self, stateMachineArn, name, input, **kwargs):
        f = utils.get_state_machine_name(stateMachineArn)
        return requests.post(
            u'http://{}'.format(f),
            json=input
        ).json()

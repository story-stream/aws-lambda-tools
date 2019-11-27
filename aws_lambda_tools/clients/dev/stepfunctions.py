import requests

from .base import Base


class StepFunctions(Base):

    def start_execution(self, stateMachineArn, name, input, **kwargs):
        from aws_lambda_tools.core import utils

        state_machine_name = utils.get_state_machine_name(stateMachineArn)

        ServicePath = self._parse_function_name(state_machine_name)

        response = requests.post(
            'http://{}'.format(ServicePath),
            json=input
        )

        # If the service does not have the path provided, call the function itself
        if response.status_code == 404:
            response = requests.post(
                'http://{}'.format(state_machine_name),
                json=input
            )

        return response.json()

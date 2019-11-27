import requests

from .base import Base


class Lambda(Base):

    def invoke(self, FunctionName, Payload, InvocationType='RequestResponse'):
        ServicePath = self._parse_function_name(FunctionName)

        response = requests.post(
            'http://{}'.format(ServicePath),
            json=Payload
        )

        # If the service does not have the path provided, call the function itself
        if response.status_code == 404:
            response = requests.post(
                'http://{}'.format(FunctionName),
                json=Payload
            )

        return response.json()

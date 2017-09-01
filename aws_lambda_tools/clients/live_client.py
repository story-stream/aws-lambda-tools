import boto3
import json


class Client(object):

    def __init__(self, *args, **kwargs):
        self._client = boto3.client(*args, **kwargs)

    def invoke(self, *args, **kwargs):
        response = self._client.invoke(*args, **kwargs)
        return json.loads(''.join(_get_payload(result['Payload'])))

    def _get_payload(self, body):
        for chunk in iter(lambda: body.read(1024), b''):
            yield chunk

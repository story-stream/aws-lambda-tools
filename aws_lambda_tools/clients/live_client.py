import boto3
import json


class Client(object):

    def __init__(self, *args, **kwargs):
        self._client = boto3.client(*args, **kwargs)

    def invoke(self, FunctionName, Payload, InvocationType='Event', **kwargs):
        if hasattr(Payload, 'iteritems'):
            Payload = json.dumps(Payload)

        response = self._client.invoke(
            FunctionName=FunctionName,
            Payload=Payload,
            InvocationType=InvocationType,
            **kwargs
        )

        return json.loads(''.join(self._get_payload(response['Payload'])))

    def _get_payload(self, body):
        for chunk in iter(lambda: body.read(1024), b''):
            yield chunk

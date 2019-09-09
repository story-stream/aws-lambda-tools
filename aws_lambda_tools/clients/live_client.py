import boto3
import json


class Client(object):

    def __init__(self, *args, **kwargs):
        self._client = boto3.client(*args, **kwargs)

    def invoke(self, FunctionName, Payload, InvocationType='RequestResponse', **kwargs):
        response = self._client.invoke(
            FunctionName=FunctionName,
            Payload=json.dumps(Payload, default=lambda x: x.isoformat() if hasattr(x, 'isoformat') else x),
            InvocationType=InvocationType,
            **kwargs
        )

        if InvocationType == 'Event':
            return

        return json.loads(''.join(self._get_payload(response['Payload'])))

    def start_execution(self, stateMachineArn, name, input, **kwargs):
        result = self._client.start_execution(
            stateMachineArn=stateMachineArn,
            name=name,
            input=json.dumps(input, default=lambda x: x.isoformat() if hasattr(x, 'isoformat') else x),
            **kwargs
        )

        return result

    def _get_payload(self, body):
        for chunk in iter(lambda: body.read(1024), b''):
            yield chunk

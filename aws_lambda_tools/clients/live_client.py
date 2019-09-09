import boto3
import json


class Client(object):

    def __init__(self, *args, **kwargs):
        self._client = boto3.client(*args, **kwargs)

    def invoke(self, FunctionName, Payload, InvocationType='RequestResponse', **kwargs):
        if hasattr(Payload, 'items') or hasattr(input, 'iteritems'):
            Payload = json.dumps(Payload, default=lambda x: x.isoformat() if hasattr(x, 'isoformat') else x)

        response = self._client.invoke(
            FunctionName=FunctionName,
            Payload=Payload,
            InvocationType=InvocationType,
            **kwargs
        )

        if InvocationType == 'Event':
            return
        
        print(response)

        return json.loads(''.join(self._get_payload(response['Payload'])))

    def start_execution(self, stateMachineArn, name, input, **kwargs):
        if hasattr(input, 'items') or hasattr(input, 'iteritems'):
            input = json.dumps(input, default=lambda x: x.isoformat() if hasattr(x, 'isoformat') else x)

        result = self._client.start_execution(
            stateMachineArn=stateMachineArn,
            name=name,
            input=input,
            **kwargs
        )

        return result

    def _get_payload(self, body):
        for chunk in iter(lambda: body.read(1024), b''):
            yield chunk

import boto3
import botocore.config
import json
import os


class Client(object):

    def __init__(self, client_type, region=None, *args, **kwargs):
        if client_type == 'lambda' and 'config' not in kwargs:
            kwargs['config'] = botocore.config.Config(
                connect_timeout=300,
                read_timeout=300,
                retries={'max_attempts': 2}
            )

        if region is None:
            region = os.environ['AWS_REGION']

        self._client = boto3.client(client_type, region, *args, **kwargs)

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

        return json.loads(response['Payload'].read().decode('utf-8'))

    def start_execution(self, stateMachineArn, name, input, **kwargs):
        if hasattr(input, 'items') or hasattr(input, 'iteritems'):
            input = json.dumps(input, default=lambda x: x.isoformat() if hasattr(x, 'isoformat') else x)

        return self._client.start_execution(
            stateMachineArn=stateMachineArn,
            name=name,
            input=input,
            **kwargs
        )

    def send_message(self, QueueUrl, MessageBody, **kwargs):
        return self._client.send_message(
            QueueUrl=QueueUrl,
            MessageBody=MessageBody,
            **kwargs
        )

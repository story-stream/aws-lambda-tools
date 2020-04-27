import boto3
import botocore.config
import json
import os


class BotoWrapper(object):
    def __init__(self, attr, pre=None, post=None):
        self.attr = attr
        self.pre = pre
        self.post = post

    def __call__(self, *args, **kwargs):
        if self.pre is not None:
            try:
                args, kwargs = self.pre(*args, **kwargs)
            except ValueError:
                pass

        result = self.attr(*args, **kwargs)

        if self.post is not None:
            return self.post(result, *args, **kwargs)

        return result


class Client(object):
    def __init__(self, client_type, region=None, config=None, *args, **kwargs):
        if client_type == 'lambda' and config is None:
            kwargs['config'] = botocore.config.Config(
                connect_timeout=300,
                read_timeout=300,
                retries={'max_attempts': 0}
            )

        if region is None:
            region = os.environ['AWS_REGION']

        self._client = boto3.client(client_type, region, *args, **kwargs)

    def __getattr__(self, name):
        attr = self._client.__getattr__(name)

        pre_func = getattr(self, f'pre_{name}', None)
        post_func = getattr(self, f'post_{name}', None)
        if pre_func is None and post_func is None:
            return attr

        return BotoWrapper(attr, pre=pre_func, post=post_func)

    def pre_invoke(self, FunctionName, Payload, *args, **kwargs):
        if hasattr(Payload, 'items') or hasattr(input, 'iteritems'):
            Payload = self._parse_payload(Payload)

        return ((FunctionName, Payload, *args), kwargs)

    def post_invoke(self, response, InvocationType='RequestResponse', *args, **kwargs):
        if InvocationType == 'Event':
            return

        return json.loads(''.join(self._parse_response(response['Payload'])))

    def pre_start_execution(self, stateMachineArn, name, input, *args, **kwargs):
        if hasattr(input, 'items') or hasattr(input, 'iteritems'):
            input = self._parse_payload(input)

        return ((stateMachineArn, name, input, *args), kwargs)

    def _parse_payload(self, data):
        return json.dumps(data, default=lambda x: x.isoformat() if hasattr(x, 'isoformat') else x)

    def _parse_response(self, body):
        for chunk in iter(lambda: body.read(1024).decode('utf-8'), b''):
            yield chunk

from .lambda_client import Lambda
from .sqs import SQS
from .stepfunctions import StepFunctions


MAPPING = {
    'lambda': Lambda,
    'stepfunctions': StepFunctions,
    'sqs': SQS,
}


def Client(client_type, *args, **kwargs):
    try:
        return MAPPING[client_type](*args, **kwargs)
    except KeyError:
        raise RuntimeError(f'Client {client_type} is not supported')

import botocore.config
import os
import uuid
import requests

from copy import deepcopy
from dpath import util
from functools import wraps


from aws_lambda_tools.clients import Client
from aws_lambda_tools.core.logging import logger


lambda_client = Client(
    'lambda', 
    os.environ['AWS_REGION'], 
    config=botocore.config.Config(
        connect_timeout=300, 
        read_timeout=300, 
        retries={'max_attempts': 0}
    )
)
step_client = Client('stepfunctions', os.environ['AWS_REGION'])


def get_state_machine_name(arn):
    return arn.split(':')[-1]


def execute(task, event, config=None, **kwargs):
    try:
        return statemachine(task, event, **kwargs)
    except ValueError:
        pass

    try:
        result = request(task, event, **kwargs)
    except ValueError:
        return task(task, event, **kwargs)
        
    merge(event, result, config=config)

    log_result(event, result, config=config)

    return None


def execute_next(tasks, event, config=None):
    while True:
        try:
            task = tasks.pop(0)
        except IndexError:
            execute(config.success, event, config=config)
            break
        
        result = execute(task, event, config=config)
        if result is not None:
            break


def statemachine(task, event, **kwargs):
    if not task.startswith('external:'):
        raise ValueError

    state_machine_arn = task[9:]

    logger.info('Executing state machine: {}'.format(state_machine_arn))

    event.update(**kwargs)

    task_result = step_client.start_execution(
        stateMachineArn=state_machine_arn,
        name=str(uuid.uuid1()),
        input=event,
    )

    logger.info('Task result: {}'.format(task_result))


def request(task, event, **kwargs):
    if not task.startswith('request:'):
        raise ValueError

    logger.info('Executing request: {}'.format(task))
    # call our load balancer
    url = task[8:]

    event.update(**kwargs)
    
    # Give a maximum of 3 attempts to get a successful response from an external service
    for i in range(3):
        response = requests.post(
            url=url,
            json=event
        )
        if response.status_code == 200:
            break
    else:
        logger.error('Request failed {}'.format(response.content))
        raise RuntimeError
    
    return response.json()


def task(task, event, sync=False, **kwargs):
    logger.info('Executing lambda function: {}'.format(task))

    event.update(**kwargs)
    
    task_result = lambda_client.invoke(
        FunctionName=task,
        Payload=event,
        InvocationType='RequestResponse' if sync else 'Event',
    )

    if 'stackTrace' in task_result:
        raise RuntimeError
    
    return task_result


def log_result(event, result, config=None):
    log_result = deepcopy(result)

    if config is not None and config.key:
        try:
            event[config.key]['task_log'].append(result)

        except (KeyError, TypeError):
            event[config.key]['task_log'] = [result]

    else:
        try:
            event['task_log'].append(result)

        except (KeyError, TypeError):
            event['task_log'] = [result]


def merge(event, result, config=None):
    if config is not None and config.key:
        try:
            util.merge(event[config.key], result)

        except (KeyError, TypeError):
            # We use the `dict` constructor or we end up updating the instance of
            # this dictionary on another iteration rather than the payload in `asset`.
            event[config.key] = dict(result)

    else:
        try:
            util.merge(event, result)

        except (KeyError, TypeError):
            # We use the `dict` constructor or we end up updating the instance of
            # this dictionary on another iteration rather than the payload in `asset`.
            event = dict(result)

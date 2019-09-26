import os
import uuid
import requests

from aws_lambda_tools.clients import Client
from contextlib import suppress
from copy import deepcopy
from dpath.util import merge

from .decorators import log


class Pipeline(object):
    lambda_client = Client('lambda', os.environ['AWS_REGION'])
    step_client = Client('stepfunctions', os.environ['AWS_REGION'])

    def __init__(self, tasks, success=None, error=None, key=None):
        self.tasks = deepcopy(tasks)
        self.success = success
        self.error = error
        self.key = key
        self.executed = []

    @log
    def execute(self, event):
        while self.tasks:
            task = self.tasks.pop(0)

            try:
                with suppress(ValueError):
                    result = self._statemachine(task, event)

                    self._log_result(event, result)

                    break

                try:
                    result = self._request(task, event)
                except ValueError:
                    result = self._task(task, event)

            except Exception as e:
                self._error(event, e)

            else:
                self._merge(event, result)

                self._log_result(event, result)

            self.executed.append(task)

        self._success(event)
        
        return event
    
    def _success(self, event):
        if self.success is not None:
            self.lambda_client.invoke(
                FunctionName=self.success,
                Payload=event,
                InvocationType='Event',
            )

    def _error(self, event, exception):
        if self.error is not None:
            event.update({'error': exception.message})

            self.lambda_client.invoke(
                FunctionName=self.error,
                Payload=event,
                InvocationType='Event',
            )
    
    def _statemachine(self, task, event, **kwargs):
        if not task.startswith('external:'):
            raise ValueError

        state_machine_arn = task[9:]

        event.update(**kwargs)

        return self.step_client.start_execution(
            stateMachineArn=state_machine_arn,
            name=str(uuid.uuid1()),
            input=event,
        )

    def _request(self, task, event, **kwargs):
        if not task.startswith('request:'):
            raise ValueError

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
            raise RuntimeError
        
        return response.json()

    def _task(self, task, event, **kwargs):
        event.update(**kwargs)
        
        task_result = self.lambda_client.invoke(
            FunctionName=task,
            Payload=event,
            InvocationType='RequestResponse',
        )

        if 'stackTrace' in task_result:
            raise RuntimeError
        
        return task_result

    def _log_result(self, event, result):
        log_result = deepcopy(result)

        if self.key:
            try:
                event[self.key]['task_log'].append(result)

            except (KeyError, TypeError):
                event[self.key]['task_log'] = [result]

        else:
            try:
                event['task_log'].append(result)

            except (KeyError, TypeError):
                event['task_log'] = [result]

    def _merge(self, event, result):
        if self.key:
            try:
                merge(event[self.key], result)

            except (KeyError, TypeError):
                # We use the `dict` constructor or we end up updating the instance of
                # this dictionary on another iteration rather than the payload in `asset`.
                event[self.key] = dict(result)

        else:
            try:
                merge(event, result)

            except (KeyError, TypeError):
                # We use the `dict` constructor or we end up updating the instance of
                # this dictionary on another iteration rather than the payload in `asset`.
                event = dict(result)

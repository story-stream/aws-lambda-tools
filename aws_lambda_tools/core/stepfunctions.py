from collections import namedtuple

from aws_lambda_tools.clients import Client
from aws_lambda_tools.core.logger import logger
from time import sleep


# BaseTask = namedtuple('BaseTask', ['name', 'type', 'next'])


# class ExecuteTask(BaseTask):
#     def __init__(self, name, task_type, next_task, function, output=None):
#         BaseTask.__init__(self, name, task_type, next_task)

#         self.output = output or '$'


# class CheckTask(BaseTask):
#     def __init__(self, name, task_type, next_task, repeat_task, next_check, repeat_check):
#         BaseTask.__init__(self, name, task_type, next_task)

#         self.repeat_task = repeat_task


# class SleepTask(BaseTask):
#     def __init__(self, name, task_type, next_task, timeout=1):
#         BaseTask.__init__(self, name, task_type, next_task)

#         self.timeout = timeout


# def raise_exception():
#     raise ValueError


# class Task(BaseTask):
#     MAPPING = {
#         'execute': ExecuteTask,
#         'check': CheckTask,
#         'sleep': SleepTask,
#         'success': '',
#         'fail': lambda *args, **kwargs: raise_exception(),
#     }

#     def __new__(cls, name, task_type, next_task, *args, **kwargs):
#         try:
#             task_cls = cls.MAPPING[task_type]
#         except KeyError:
#             raise ValueError(f'Type {type} is not supports, valid options are')

#         task = task_cls.__new__(cls, name, task_type, next_task, *args, **kwargs)
#         task.__init__(name, task_type, next_task, *args, **kwargs)

#         return task


# start = Task(
#     name='Storage',
#     task_type='execute',
#     next_task='Wait 1 Minute',
#     function='vimeo-storage',
#     output='$.video',
# )
# wait = Task(
#     name='Wait 1 Minute',
#     task_type='sleep',
#     next_task='Check Status',
#     timeout=60,
# )
# check = Task(
#     name='Check Status',
#     task_type='check',
#     next_task='',
#     repeat_task='Wait 1 Minute',
#     function='vimeo-check',
#     output='$.video',
#     next_check=Check(field='status', value='available'),
#     repeat_check=Check(field='status', value='error'),
# )


Task = namedtuple(
    'Task',
    ['name', 'function', 'repeat', 'success', 'error', 'output', 'timeout', 'max_checks'],
    defaults=(False, None, None, None, 1, 1),
)

Check = namedtuple('Check', ['field', 'value'])

Functions = namedtuple('Functions', ['tasks', 'success', 'error'], defaults=(None, None))


functions = Functions(
    [
        Task(
            'Storage',
            'vimeo-storage',
            output='$.video',
        ),
        Task(
            'Check Status',
            'vimeo-check',
            repeat=True,
            success=Check(field='status', value='available'),
            error=Check(field='status', value='error'),
            output='$.video',
            timeout=60,
            max_checks=60
        ),
    ],
    success=Task(
        'Success',
        'vimeo-success',
    ),
    error=Task(
        'Error',
        'vimeo-error',
        output='$.error',
    ),
)

lambda_client = Client('lambda')


def stepfunction(functions):
    return lambda payload, *args: _execute(functions, payload, *args)


def _execute(functions, payload, *args):
    for task in functions.tasks:
        logger.info('Executing task: {}'.format(task))

        if task.repeat:
            # Wait for 60 seconds before doing the first check.
            sleep(task.timeout)

            for i in range(task.max_checks):
                logger.info('Performing check {} of {}'.format(i + 1, task.max_checks))

                # While the payload is updated with the status, we surface it to make things easier to read.
                result = lambda_client.invoke(
                    FunctionName=task.name,
                    Payload=payload,
                    InvocationType='RequestResponse',
                )

                if task.error:
                    value = result[task.error.field]

                    if value == task.error.value:
                        logger.warn('Error checking for result: {}'.format(result))

                        if task.output and task.output != '$':
                            target = payload
                            for field in task.output.split('.'):
                                target = target[field]

                            target = value

                        else:
                            payload = value

                        if functions.error is not None:
                            lambda_client.invoke(
                                FunctionName=functions.error.name,
                                Payload=payload,
                                InvocationType='Event',
                            )

                        raise ValueError('Error checking for result: {}'.format(payload))

                if task.success:
                    value = result[task.success.field]

                    if task.output and task.output != '$':
                        target = payload
                        for field in task.output.split('.'):
                            target = target[field]

                        target = result

                    else:
                        payload = result

                    if value == task.success.value:
                        logger.info('Success')
                        break

                sleep(task.timeout)

            else:
                raise ValueError('Exceeded maximum checks')

        else:
            result = lambda_client.invoke(
                FunctionName=task.name,
                Payload=payload,
                InvocationType='RequestResponse',
            )

            if task.output and task.output != '$':
                target = payload
                for field in task.output.split('.'):
                    target = target[field]

                target = result

            else:
                payload = result

        logger.info('Payload after task {}: {}'.format(task, payload))

    logger.info('All tasks completed: {}'.format(payload))

    if functions.success is not None:
        lambda_client.invoke(
            FunctionName=functions.success.name,
            Payload=payload,
            InvocationType='Event',
        )


__all__ = [
    'Functions',
    'Task',
    'Check',
    'stepfunction'
]
import os
import requests


def request(self, **data):
    response = requests.post(
        'http://local-aws/{}/'.format(self.endpoint),
        json=data,
    )

    return response.json()


class Base(object):
    endpoint = ''
    functions = ()

    def __init__(self, *args, **kwargs):
        if not self.endpoint:
            raise RuntimeError('Must specify endpoint for client {}'.format(self.__class__))

        if not self.functions:
            raise RuntimeError('Must specify functions for client {}'.format(self.__class__))

    def __getattr__(self, name):
        if name not in self.functions:
            raise AttributeError('{} has no attribute {}'.format(self.__class__, name))

        return lambda x: request(**x)

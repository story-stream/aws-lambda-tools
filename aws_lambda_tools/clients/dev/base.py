import os


class Base(object):

    def __init__(self, *args, **kwargs):
        pass

    def _parse_function_name(self, function_name):
        try:
            available_services = os.environ['STORYSTREAM_SERVICES']
        except KeyError:
            return function_name

        for service in available_services.split(','):
            if function_name.startswith(service):
                route = function_name[len(service) + 1:]

                return f'{service}/{route}'

        return function_name

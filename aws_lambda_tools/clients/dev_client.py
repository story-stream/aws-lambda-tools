import requests


class Client(object):

    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)

    def invoke(self, FunctionName, Payload, InvocationType='RequestResponse'):
        return requests.post(
            u'http://{}'.format(FunctionName),
            json=Payload
        ).json()

import requests

from .base import Base


class SQS(Base):

    def send_message(self, QueueUrl, MessageBody, MessageAttributes=None, **kwargs):
        ServicePath = self._parse_function_name(QueueUrl)

        MessageAttributes = MessageAttributes or {}
        data = {
            'Records': [{
                'MessageAttributes': {
                    key: {
                        'stringValue': value['StringValue'],
                        'dataType': value['DataType'],
                    }
                    for key, value in MessageAttributes.items()
                },
                'MessageBody': MessageBody,
            }]
        }

        response = requests.post(
            u'http://{}'.format(ServicePath),
            json=data
        )

        # If the service does not have the path provided, call the function itself
        if response.status_code == 404:
            response = requests.post(
                u'http://{}'.format(QueueUrl),
                json=data
            )

        return response.json()

from .base import Base


class SQS(Base):
    endpoint = 'aws-sqs'
    functions = ('send_message',)

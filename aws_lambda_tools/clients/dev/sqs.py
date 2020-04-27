from .base import Base


class SQS(Base):
    endpoint = 'sqs'
    functions = ('send_message',)

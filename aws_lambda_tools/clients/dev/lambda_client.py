import requests

from .base import Base


class Lambda(Base):
    endpoint = 'aws-lambda'
    functions = ('invoke',)

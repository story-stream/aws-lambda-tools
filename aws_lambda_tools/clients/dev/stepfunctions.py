import requests

from .base import Base


class StepFunctions(Base):
    endpoint = 'stepfunctions'
    functions = ('start_execution',)

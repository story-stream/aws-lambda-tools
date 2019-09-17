import os
import unittest


class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        os.environ['AWS_REGION'] = 'test'

        from aws_lambda_tools.core import utils
        self.utils = utils

    def test_get_state_machine_name_returns_name_from_arn(self):
        arn = 'arn:aws:states:eu-west-1:754902810601:stateMachine:video-processing'
        expected = 'video-processing'
        actual = self.utils.get_state_machine_name(arn)
        self.assertEqual(actual, expected)

import boto3
import unittest
from aws_lambda_tools.clients.live_client import Client
from mock import patch, MagicMock


class LiveClientBaseTestCase(unittest.TestCase):

    @patch('aws_lambda_tools.clients.live_client.boto3.client', spec=True)
    def test_creates_boto_client_instance_with_provided_params(self, mock_client):
        target = Client(clive=False, dave=True)
        client = target._client

        mock_client.assert_called_once_with(clive=False, dave=True)


class LiveClientInvokeTestCase(unittest.TestCase):

    def setUp(self):
        self.client = MagicMock()
        client_patch = patch('aws_lambda_tools.clients.live_client.boto3.client', return_value=self.client)
        client_patch.start()
        self.addCleanup(client_patch.stop)

        self.target = Client()
        self.target._client = self.client
        self.target._get_payload = MagicMock()
        self.target._get_payload.side_effect = lambda x: x

        self.client.invoke.return_value = {
            'Payload': '{"result": "ok"}',
        }

    def test_calls_client_invoke_with_provided_parameters(self):
        self.target.invoke(
            FunctionName='testing',
            Payload='{"test": true}',
            InvocationType='Testing',
        )

        self.client.invoke.assert_called_once_with(
            FunctionName='testing',
            Payload='{"test": true}',
            InvocationType='Testing'
        )

    def test_converts_dictionary_payload_into_json(self):
        self.target.invoke(
            FunctionName='testing',
            Payload={'test': True},
            InvocationType='Testing',
        )

        self.client.invoke.assert_called_once_with(
            FunctionName='testing',
            Payload='{"test": true}',
            InvocationType='Testing'
        )

    def test_returns_result_as_a_dictionary(self):
        self.target._get_payload.return_value = '{"result": "ok"}'

        expected = {'result': 'ok'}

        actual = self.target.invoke(
            FunctionName='testing',
            Payload={'test': True},
            InvocationType='Testing',
        )

        self.assertEqual(actual, expected)

    def test_defaults_invocation_type_to_request_response(self):
        self.target.invoke(
            FunctionName='testing',
            Payload={'test': True},
        )

        expected = 'RequestResponse'

        actual = self.client.invoke.call_args_list[0][1]['InvocationType']

        self.assertEqual(actual, expected)

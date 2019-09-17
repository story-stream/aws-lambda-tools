import boto3
import base64
import json
import os
from botocore.exceptions import ClientError


def secret(name):
    if not name.startswith('secret:'):
        return name
    
    name = name[7:]
    
    # Use this code snippet in your app.
    # If you need more information about configurations or implementing the sample code, visit the AWS docs:   
    # https://aws.amazon.com/developers/getting-started/python/
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=os.environ['AWS_REGION']
    )

    for i in range(3):
        try:
            response = client.get_secret_value(
                SecretId=name
            )
            break
        except ClientError as e:
            pass

    # Decrypts secret using the associated KMS CMK.
    # Depending on whether the secret is a string or binary, one of these fields will be populated.
    if 'SecretString' in response:
        try:
            secret = json.loads(response['SecretString'])
        except json.decoder.JSONDecodeError:
            return response['SecretString']
        else:
            return secret[name]

    return base64.b64decode(response['SecretBinary'])

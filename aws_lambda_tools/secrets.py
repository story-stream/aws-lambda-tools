import boto3
import base64
import json
from botocore.exceptions import ClientError


def secret(name):
    if not name.startswith('secret:'):
        return name
    
    name = name[7:]
    
    # Use this code snippet in your app.
    # If you need more information about configurations or implementing the sample code, visit the AWS docs:   
    # https://aws.amazon.com/developers/getting-started/python/
    region_name = "eu-west-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    for i in range(3):
        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=name
            )
            break
        except ClientError as e:
            pass

    # Decrypts secret using the associated KMS CMK.
    # Depending on whether the secret is a string or binary, one of these fields will be populated.
    if 'SecretString' in get_secret_value_response:
        try:
            secret = json.loads(get_secret_value_response['SecretString'])
        except json.decoder.JSONDecodeError:
            return get_secret_value_response['SecretString']
        else:
            return secret[name]

    return base64.b64decode(get_secret_value_response['SecretBinary'])

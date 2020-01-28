def aws_lambda():
    from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

    return AwsLambdaIntegration()


INTEGRATION_MAPPING = {
    'lambda': aws_lambda
}


def configure(integration='lambda'):
    import os

    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    if not SENTRY_DSN:
        from aws_lambda_tools.core.logger import logger

        logger.warning('Sentry is not configured')

        return

    import sentry_sdk

    try:
        integration = INTEGRATION_MAPPING[integration]()
    except KeyError:
        integration = aws_lambda()

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[integration],
    )


__all__ = [
    'configure',
]
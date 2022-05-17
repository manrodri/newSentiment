from aws_cdk import (
    core as cdk,
    aws_lambda as lambda_,
)



class LambdaStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        lambda_.Function(self, "MyFunction",
            code=lambda_.Code.from_asset('fetchNews'),
            runtime=lambda_.Runtime.PYTHON_3_8,  # required
            handler="lambda_function.lambda_handler"
        )


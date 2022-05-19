from aws_cdk import (
    core as cdk,
    aws_lambda as lambda_,
    aws_lambda_python as python_lambda,
    aws_apigateway as apigw,
    aws_iam as iam
)
from aws_cdk.aws_lambda import Runtime


class LambdaStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        fetch_news_lambda = lambda_.Function(self, "FetchNewsFunction",
                                             code=lambda_.Code.from_asset('fetchNews'),
                                             runtime=lambda_.Runtime.PYTHON_3_8,  # required
                                             handler="lambda_function.lambda_handler"
                                             )

        insert_news_lambda = python_lambda.PythonFunction(self, "InsertNewsFunction",
                                                          entry="./getNews",  # required
                                                          runtime=Runtime.PYTHON_3_8,  # required
                                                          index="getNews.py",  # optional, defaults to 'index.py'
                                                          handler="lambda_handler",
                                                          environment={
                                                              'API_KEY': "foo",

                                                          }
                                                          )

        role = insert_news_lambda.role
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("ComprehendFullAccess"))

        fetch_role = fetch_news_lambda.role
        fetch_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"))

        news_api = apigw.LambdaRestApi(
            self, 'Endpoint',
            rest_api_name="news_sentiment_api",
            handler=fetch_news_lambda,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS
            )
        )
        news = news_api.root.add_resource("news")
        news.add_method("POST")

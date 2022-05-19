from aws_cdk import (
    core as cdk,
    aws_lambda as lambda_,
    aws_lambda_python as python_lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_ssm as ssm,
    aws_dynamodb as dynamodb
)

from aws_cdk.aws_iam import Role, ServicePrincipal, PolicyStatement
from aws_cdk.aws_dynamodb import AttributeType, Attribute
from aws_cdk.aws_lambda import Runtime
from aws_cdk import core, aws_events, aws_events_targets


class CdkStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # news_api_key = ssm.StringParameter.from_secure_string_parameter_attributes(self, "MyValue",
        #                                                               parameter_name="/prod/newsAPIKey",
        #                                                               version=1,
        #                                                               ).string_value
        #  NOT SUPPORTED: USE SECRETS MANAGER??

        # The code that defines your stack goes here

        news_table = dynamodb.Table(self, "Table",
                                    partition_key=Attribute(name="sentiment", type=AttributeType.STRING),
                                    sort_key=Attribute(name='time', type=AttributeType.STRING),
                                    write_capacity=1,
                                    read_capacity=1,
                                    )

        fetch_news_lambda = lambda_.Function(self, "FetchNewsFunction",
                                             code=lambda_.Code.from_asset('fetchNews'),
                                             runtime=lambda_.Runtime.PYTHON_3_8,  # required
                                             handler="lambda_function.lambda_handler",
                                             environment={
                                                 'TABLE_NAME': news_table.table_name
                                             }
                                             )

        insert_news_lambda = python_lambda.PythonFunction(self, "InsertNewsFunction",
                                                          entry="./getNews",  # required
                                                          runtime=Runtime.PYTHON_3_8,  # required
                                                          index="getNews.py",  # optional, defaults to 'index.py'
                                                          handler="lambda_handler",
                                                          timeout=cdk.Duration.seconds(30),
                                                          environment={
                                                              'API_KEY': "aea8a6afc5984e578974e669ade1b8d7",
                                                              'TABLE_NAME': news_table.table_name
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

        lambda_schedule = aws_events.Schedule.rate(core.Duration.days(1))
        event_lambda_target = aws_events_targets.LambdaFunction(handler=insert_news_lambda)
        lambda_cw_event = aws_events.Rule(
            self,
            "Rule_ID_Here",
            description=
            "The once per day CloudWatch event trigger for the Lambda",
            enabled=True,
            schedule=lambda_schedule,
            targets=[event_lambda_target])

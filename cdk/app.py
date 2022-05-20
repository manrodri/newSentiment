#!/usr/bin/env python3
import os
from aws_cdk import core

from cdk.cdk_stack import CdkStack
from cdk.s3 import S3Stack
from cdk.frontend_pipeline import CodePipelineFrontendStack

REGION = os.getenv('CDK_REGION')
ACCOUNT = os.getenv('CDK_ACCOUNT')

app = core.App()

s3_stack = S3Stack(app, 's3buckets', env=core.Environment(account=ACCOUNT, region=REGION))
cp_frontend = CodePipelineFrontendStack(
    app,
    'cp-frontend',
    frontendBucket=core.Fn.import_value('frontend-bucket'),
    env=core.Environment(account=ACCOUNT, region=REGION)
)


CdkStack(app, "CdkStack",
         env=core.Environment(account=ACCOUNT, region=REGION),
         )

app.synth()

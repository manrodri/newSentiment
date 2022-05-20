from aws_cdk import (
    aws_ssm as ssm,
    aws_s3 as s3,
    aws_iam as iam,
    core
)


class S3Stack(core.Stack):
    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id)

        account_id = core.Aws.ACCOUNT_ID
        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        # create an S3 bucket
        lambda_bucket = s3.Bucket(self, 'lambda-bucket',
                                  access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
                                  encryption=s3.BucketEncryption.S3_MANAGED,
                                  block_public_access=s3.BlockPublicAccess(
                                      block_public_acls=True,
                                      block_public_policy=True,
                                      ignore_public_acls=True,
                                      restrict_public_buckets=True
                                  ),
                                  removal_policy=core.RemovalPolicy.DESTROY
                                  )

        ssm.StringParameter(self, 'ssm-lambda-bucket',
                            parameter_name='/' + env_name + '/lambda-s3-bucket',
                            string_value=lambda_bucket.bucket_name
                            )

        # pipeline artifacts bucket
        artifacts_bucket = s3.Bucket(self, 'artifact-bucket',
                                     access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
                                     encryption=s3.BucketEncryption.S3_MANAGED,
                                     block_public_access=s3.BlockPublicAccess(
                                         block_public_acls=True,
                                         block_public_policy=True,
                                         ignore_public_acls=True,
                                         restrict_public_buckets=True
                                     ),
                                     removal_policy=core.RemovalPolicy.DESTROY
                                     )
        core.CfnOutput(self, 's3-build-artifacts-export',
                       value=artifacts_bucket.bucket_name,
                       export_name='build-artifacts-bucket')

        # frontend bucket
        artifacts_bucket = s3.Bucket(self, 'frontend',
                                     access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
                                     encryption=s3.BucketEncryption.S3_MANAGED,
                                     public_read_access=True,
                                     website_index_document='index.html',
                                     removal_policy=core.RemovalPolicy.DESTROY
                                     )
        core.CfnOutput(self, 'frontend-bucket-export',
                       value=artifacts_bucket.bucket_name,
                       export_name='frontend-bucket')
        core.CfnOutput(self, f'frontend-{env_name}-dns-name',
                       value=artifacts_bucket.bucket_website_domain_name,
                       export_name='front-end-url')
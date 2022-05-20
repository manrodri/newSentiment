from aws_cdk import (
    aws_s3 as s3,
    aws_ssm as ssm,
    aws_codepipeline as cp,
    aws_codepipeline_actions as cp_actions,
    aws_codecommit as ccm,
    aws_codebuild as cb,
    aws_iam as iam,
    core
)


class CodePipelineFrontendStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, frontendBucket, **kwargs):
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context('project_name')
        env_name = self.node.try_get_context('env')

        webhosting_buket = s3.Bucket.from_bucket_name(self, 'webhostingbucket-id', bucket_name=frontendBucket)
        cdn_id = ssm.StringParameter.from_string_parameter_name(self, 'cdn_id',
                                                                string_parameter_name=f'/{env_name}/cdn-id')

        source_repo = ccm.Repository.from_repository_name(self, 'repository-id', repository_name='simple_life_site')

        artifact_bucket = s3.Bucket(self, 'artifactbucket',
                                    encryption=s3.BucketEncryption.S3_MANAGED,
                                    access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL
                                    )
        pipeline = cp.Pipeline(self, 'frontend-pipeline',
                               pipeline_name=f'{prj_name}-{env_name}-frontend-pipeline',
                               artifact_bucket=artifact_bucket,
                               restart_execution_on_update=False
                               )
        source_output = cp.Artifact(artifact_name='source')
        build_output = cp.Artifact(artifact_name='build')

        build_project = cb.Project(self, 'buildproject',
                                   project_name=f'{env_name}-{prj_name}-build-project',
                                   environment=cb.BuildEnvironment(
                                       build_image=cb.LinuxBuildImage.STANDARD_3_0,
                                       environment_variables={
                                           'ENV': cb.BuildEnvironmentVariable(value='dev'),
                                           'PRJ': cb.BuildEnvironmentVariable(value=prj_name),
                                           'STAGE': cb.BuildEnvironmentVariable(value='dev')
                                       }
                                   ),
                                   build_spec=cb.BuildSpec.from_object(
                                       {
                                           'version': '0.2',
                                           'phases': {
                                               'install': {
                                                   'commands': [
                                                       'echo --INSTALL PHASE--',
                                                       f'aws s3 sync . s3://{webhosting_buket.bucket_name}'
                                                   ]
                                               }
                                           }
                                       }
                                   )
                                   )

        build_project.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess')
        )

        pipeline.add_stage(stage_name='Source',
                           actions=[
                               cp_actions.CodeCommitSourceAction(
                                   action_name='CodeCommitSource',
                                   repository=source_repo,
                                   branch='master',
                                   output=source_output
                               )
                           ])

        pipeline.add_stage(
            stage_name='Deploy',
            actions=[
                cp_actions.CodeBuildAction(
                    action_name='DeployToDev',
                    input=source_output,
                    project=build_project,
                    outputs=[build_output]
                )
            ]
        )

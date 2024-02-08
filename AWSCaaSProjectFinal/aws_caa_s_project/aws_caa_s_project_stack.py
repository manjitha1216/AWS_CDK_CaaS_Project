# Import necessary constructs from AWS CDK and AWS services
from aws_cdk import (
    CfnOutput,
    aws_secretsmanager as secretsmanager,
    Duration,
    aws_eks as aws_eks,
    Stack,
    aws_ec2 as ec2,
    aws_iam as aws_iam,
    aws_rds as rds,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    RemovalPolicy
)
from constructs import Construct
from aws_cdk.aws_sns import (
    Topic  
)
from aws_cdk.aws_sqs import (
    Queue   
)
from aws_cdk.aws_sns_subscriptions import (
    SqsSubscription,
    EmailSubscription
)
from aws_cdk.aws_cloudwatch import (
    Alarm,
    Metric
)
from aws_cdk.aws_cloudwatch_actions import (
    AutoScalingAction,
    SnsAction
)
from aws_cdk.aws_sns import (
    Topic  
)
from aws_cdk.aws_sqs import (
    Queue   
)
from aws_cdk.aws_sns_subscriptions import (
    SqsSubscription,
    EmailSubscription
)
from aws_cdk.aws_logs import (
    LogGroup,
    LogStream
)

# Define a CloudFormation stack named AwsCaaSProjectStack
class AwsCaaSProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        availability_zones = ['eu-central-1a', 'eu-central-1b'] # Define the availability zones

        # Creation of custom VPC
        vpc = ec2.Vpc(self, 'Vpc',
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            vpc_name='eks-vpc',
            enable_dns_hostnames=True,
            enable_dns_support=True,
            availability_zones=availability_zones,
            subnet_configuration=[
                 # Subnet for public resources accessible from the internet
                ec2.SubnetConfiguration(
                    name='eks-subnet-public',
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                # Subnet for private resources with internet access for outbound traffic
                ec2.SubnetConfiguration(
                    name='eks-subnet-private',
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                # Subnet for private resources isolated from the internet
                ec2.SubnetConfiguration(
                    name='eks-subnet-privateRDS',
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ]
        )

        #    #security group for node group
        # eks_nodegroup_security_group = ec2.SecurityGroup(
        #     self, 'MyNodegroupSecurityGroup',
        #     vpc=vpc,  # Use the VPC created earlier
        #     allow_all_outbound=True  # Adjust outbound rules based on your requirements
        # )

        # # Allow inbound connections on the HTTPS ports
        # eks_nodegroup_security_group.add_ingress_rule(
        #     peer=ec2.Peer.ipv4('0.0.0.0/0'),
        #     connection=ec2.Port.tcp(443),
        #     description='Allow inbound https connections'
        # )

        #  # Allow inbound connections on the SSH ports
        # eks_nodegroup_security_group.add_ingress_rule(
        #     peer=ec2.Peer.ipv4('0.0.0.0/0'),
        #     connection=ec2.Port.tcp(22),
        #     description='Allow inbound ssh connections'
        # )

        # # Create an IAM Role to be assumed by admins
        # masters_role = aws_iam.Role(
        #     self,
        #     'EksMastersRole',
        #     assumed_by=aws_iam.AccountRootPrincipal() 
        # )

        # # Attach an IAM Policy to that Role so users can access the Cluster
        # masters_role_policy = aws_iam.PolicyStatement(
        #     actions=['eks:DescribeCluster'],
        #     resources=['*'],  # Adjust the resource ARN if needed
        # )
        # masters_role.add_to_policy(masters_role_policy)
        # cluster.aws_auth.add_masters_role(masters_role)

        # # Add the user to the cluster's admins
        # admin_user = aws_iam.User.from_user_arn(self, "AdminUser",user_arn="arn:aws:iam::757516528332:user/cdk-project")
        # cluster.aws_auth.add_user_mapping(admin_user, groups=["system:masters"])

        # # Output the EKS cluster name
        # core.CfnOutput(
        # self,
        # 'ClusterNameOutput',
        # value=cluster.cluster_name,
        # )

        # #Output the EKS master role ARN
        # core.CfnOutput(
        # self,
        # 'ClusterMasterRoleOutput',
        # value=masters_role.role_arn,
        # description="IAM Role ARN for EKS cluster administrator",  # Add a description for clarity
        # )

        #  #Creation of AWS EKS cluster
        # cluster = aws_eks.Cluster(
        #       self, 'EKS-Cluster',
        #       cluster_name='eks-cluster',
        #       version=aws_eks.KubernetesVersion.V1_28,
        #       vpc=vpc,
        #       default_capacity=0
        #   )
        
        # Create an IAM Role to be assumed by admins
        masters_role = aws_iam.Role(
            self,
            'EksMastersRole',
            assumed_by=aws_iam.AccountRootPrincipal()
        )

        # Attach an IAM Policy to that Role so users can access the Cluster
        masters_role_policy = aws_iam.PolicyStatement(
            actions=['eks:DescribeCluster'],
            resources=['*'],  # Adjust the resource ARN if needed
        )
        masters_role.add_to_policy(masters_role_policy)

        # Define the cluster
        cluster = aws_eks.Cluster(
            self, 'EKS-Cluster',
            cluster_name='eks-cluster',
            version=aws_eks.KubernetesVersion.V1_28,
            vpc=vpc,
            default_capacity=2
        )

        # Add the masters role to the cluster
        cluster.aws_auth.add_masters_role(masters_role)

        # Add the user to the cluster's admins
        admin_user = aws_iam.User.from_user_arn(self, "AdminUser", user_arn="arn:aws:iam::757516528332:user/cdk-project")
        cluster.aws_auth.add_user_mapping(admin_user, groups=["system:masters"])

        # # Output the EKS cluster name
        CfnOutput(
         self,
         'ClusterNameOutput',
         value=cluster.cluster_name,
         )

         #Output the EKS master role ARN
        CfnOutput(
         self,
         'ClusterMasterRoleOutput',
         value=masters_role.role_arn,
         description="IAM Role ARN for EKS cluster administrator",  # Add a description for clarity
         )
        
        
        #          # IAM Role for the node group
        # aws_eks.nodegroup_role = aws_iam.Role(
        #       self, 'NodegroupRole',
        #       assumed_by=aws_iam.ServicePrincipal('ec2.amazonaws.com'),
        #       managed_policies=[aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEKSWorkerNodePolicy')]
        #   ) 

        #  # # Creation of the EKS node group
        nodegroup = cluster.add_nodegroup_capacity(
              'Nodegroup',
              instance_types=[ec2.InstanceType('t3.medium')],
              desired_size=1,
              min_size=1,
              max_size=3,
              ami_type=aws_eks.NodegroupAmiType.AL2_X86_64
          )
    
    
        #Define an email address for notification
        email_address = "nataliya.maroz@accenture.com"     
        
        # Create SNS topics for EKS and RDS
        eks_sns_topic = Topic(self, 'EKS SNS topic',display_name='EKS topic')
        rds_sns_topic = Topic(self, 'RDS SNS topic',display_name='RDS topic')

        # eks_sqs_queue = Queue(self, 'EKSSQSQueue')
        # rds_sqs_queue = Queue(self, 'RDSSQSQueue')
        
        # eks_sns_topic.add_subscription(SqsSubscription(eks_sqs_queue))
        # rds_sns_topic.add_subscription(SqsSubscription(rds_sqs_queue))
        
        # Add email subscriptions to the SNS topics
        eks_sns_topic.add_subscription(EmailSubscription(email_address))
        rds_sns_topic.add_subscription(EmailSubscription(email_address))
        
        # Create a security group for the RDS instance
        rds_security_group = ec2.SecurityGroup(
            self, 'RDSSecurityGroup',
            vpc=vpc,  # Use the VPC created earlier
            allow_all_outbound=True  # Adjust outbound rules based on your requirements
        )

        # Allow inbound connections on the MySQL port (3306)
        rds_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4('0.0.0.0/0'), 
            connection=ec2.Port.tcp(3306),
            description='Allow inbound MySQL connections'
        )

        #RDS Instance Deployment
        myDB = rds.DatabaseInstance(self, 
                                    "MyDatabase",
                                    engine= rds.DatabaseInstanceEngine.MYSQL,
                                    vpc= vpc,
                                    vpc_subnets= ec2.SubnetSelection(
                                        #subnet_type= ec2.SubnetType.PUBLIC,
                                        subnet_type= ec2.SubnetType.PRIVATE_ISOLATED,
                                    ),
                                    security_groups=[rds_security_group],
                                    credentials= rds.Credentials.from_generated_secret("Admin"),
                                    instance_type= ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3,
                                                                       ec2.InstanceSize.MICRO),
                                    port= 3306,
                                    allocated_storage= 20,
                                    multi_az= True,
                                    removal_policy= RemovalPolicy.DESTROY,
                                    cloudwatch_logs_exports=['error', 'general', 'slowquery', 'audit'], #comment if db is not deployed
                                    deletion_protection= False,
                                    publicly_accessible= False
                                    )

    # #     Uncomment this section after deployment of RDS to deploy WordPress inside node group
    #     aws_eks.wordpress_chart = aws_eks.HelmChart(
    #          self, 'WordPressChart',
    #          chart='wordpress',
    #          release='wordpress',
    #          repository='https://charts.bitnami.com/bitnami',
    #          namespace='default',
    #          values={
    #              'mariadb.enabled': False,
    #              'externalDatabase.host': 'arn:aws:iam::757516528332:role/AwsCaaSProjectStack-EksMastersRoleD1AE213C-DwZ5b2TNeDCX',  # RDS endpoint
    #              'externalDatabase.user': 'Admin',   # RDS username
    #              'externalDatabase.password': '.n7b85qOCC7lUCOOlsOU-J9L9_-0m-', # RDS password
    #          },
    #          cluster=cluster
    #      )

        # Output the RDS endpoint for reference
        CfnOutput(self, 'RDS-Endpoint', value=myDB.db_instance_endpoint_address)
        CfnOutput(self, "RDSInstanceArn", value=myDB.instance_arn)

        # Define CloudWatch alarms for RDS metrics
        rds_cpu_alarm = Alarm(
            self, 'RDSCPUAlarm',
            metric=myDB.metric_cpu_utilization(),
            threshold=40,                   #triggered if the CPU utilization exceeds 90%.
            evaluation_periods=1,           #how many times the line will be crossed until alarm rings
            alarm_name='RDSCPUHighAlarm',
            actions_enabled=True
        )
        
        rds_db_connection_alarm = Alarm(
            self, 'RDSConnectionsEvent',
            metric=myDB.metric_database_connections(),
            threshold=50,                   #triggered if the CPU utilization exceeds 90%.
            evaluation_periods=1,           #how many times the line will be crossed until alarm rings
            alarm_name='RDSConnectionsEvent',
            actions_enabled=True
        )
        

        # Subscribe SNS topics to CloudWatch alarms
        rds_cpu_alarm.add_alarm_action(SnsAction(rds_sns_topic)) #subscribe sns topic to cloudwatch alarm
        rds_db_connection_alarm.add_alarm_action(SnsAction(rds_sns_topic))

        # # Create CloudWatch Logs for RDS
        # rds_log_group = LogGroup(self, "RDSLogGroup",
        #                           log_group_name="/rds/log/group",
        #                           removal_policy=RemovalPolicy.DESTROY)

        # rds_log_stream = LogStream(self, "RDSLogStream",
        #                             log_group=rds_log_group,
        #                             log_stream_name="rds_log_stream")
    
        #Configure RDS to Use Log Streams (check AWS RDS documentation)
        #Output the CloudWatch Logs Log Group and Log Stream ARNs
        # CfnOutput(self, "LogGroupArn", value=rds_log_group.log_group_arn)
        # CfnOutput(self, "LogStreamName", value=rds_log_stream.log_stream_name)
     

#         #S3 bucket creation
#         log_export_bucket = s3.Bucket(
#             self, 'LogExportBucket' , 
#             bucket_name='logexportbucket5')
        
#         # Define the bucket policy
#         bucket_policy = {
#             "Version": "2012-10-17",
#             "Statement": [
#                 {
#                     "Sid": "uploadlogsmanjitha",
#                     "Effect": "Allow",
#                     "Principal": {
#                         "Service": "logs.eu-central-1.amazonaws.com"
#                     },
#                     "Action": "s3:GetBucketAcl",
#                     "Resource": log_export_bucket.bucket_arn
#                 },
#                 {
#                     "Sid": "uploadlogs",
#                     "Effect": "Allow",
#                     "Principal": {
#                         "Service": "logs.eu-central-1.amazonaws.com"
#                     },
#                     "Action": "s3:PutObject",
#                     "Resource": log_export_bucket.bucket_arn
#                 }
#             ]
#         }

#         # # Attach the bucket policy to the S3 bucket
#         # s3.BucketPolicy(
#         #     self, 'LogsBucketPolicy',
#         #     bucket=log_export_bucket,
#         #     policy_document=aws_iam.PolicyDocument.from_json(bucket_policy)
#         # )

# ############################################################################################################################################

#         # Create an IAM role for the Lambda function
#         lambda_role = aws_iam.Role(
#             self, 'LambdaExecutionRole',
#             assumed_by=aws_iam.ServicePrincipal('lambda.amazonaws.com'),
#             managed_policies=[
#                 aws_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
#                 aws_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaRole'),
#                 aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'),
#                 aws_iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchFullAccess')
#             ]
#         )

#         # Create the Lambda function
#         export_logs_lambda = lambda_.Function(

#             self,
#             "LogsLambdaFunction",
#             handler="lambda_handler.handler",
#             runtime=lambda_.Runtime.PYTHON_3_8,
#             code=lambda_.Code.from_asset("lambda"),
#             role=lambda_role
#         )

#         # Create an Event Rule to trigger the Lambda function daily
#         # event_rule = events.Rule(
#         #     self, 'ExportLogsEventRule',
#         #     schedule=events.Schedule.cron(hour='14', minute='35')
#         # )

#         # event_rule.add_target(targets.LambdaFunction(export_logs_lambda))





#         # #S3 Bucket Creation
#         # logs_bucket = s3.Bucket(self, "LogsBucket")

#         # #Create Lambda function to send logs to S3
#         # logs_lambda_function = lambda_.Function(
#         #     self,
#         #     "LogsLambdaFunction",
#         #     handler="lambda_handler.handler",
#         #     runtime=lambda_.Runtime.PYTHON_3_8,
#         #     code=lambda_.Code.from_asset("lambda"),  # Update this path as needed
#         #     environment={
#         #         "S3_BUCKET_NAME": logs_bucket.bucket_name,
        #         "LOG_GROUP_NAME": rds_log_group.log_group_name,
        #         "LOG_STREAM_NAME": rds_log_stream.log_stream_name,
        #     },
        # )

        # logs_lambda_function.role.add_to_policy(
        #         aws_iam.PolicyStatement(y

        #                 actions=["logs:CreateLogStream", "logs:PutLogEvents"],
        #                 resources=[rds_log_group.log_group_arn + ":*"]
        #         )
        # )


        # #Grant Lambda permissions to access CloudWatch Logs and write to S3
        # rds_log_group.grant_read(logs_lambda_function)
        # logs_bucket.grant_write(logs_lambda_function)

        # #Output the S3 bucket name
        # CfnOutput(self, "LogsBucketName", value=logs_bucket.bucket_name)  
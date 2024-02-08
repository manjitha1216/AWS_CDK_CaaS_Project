import boto3
import os
import datetime

GROUP_NAME = "/aws/rds/instance/awscaasprojectstack-mydatabase1e2517db-ljeqsyoosnfl/error"
DESTINATION_BUCKET = "logsbucketmanjitha"
PREFIX = "Cloudwatchlogstest"
NDAYS = 1
nDays = int(NDAYS)


currentTime = datetime.datetime.now()
StartDate = currentTime - datetime.timedelta(days=nDays)
EndDate = currentTime - datetime.timedelta(days=nDays - 1)


fromDate = int(StartDate.timestamp() * 1000)
toDate = int(EndDate.timestamp() * 1000)

BUCKET_PREFIX = os.path.join(PREFIX, StartDate.strftime('%Y{0}%m{0}%d').format(os.path.sep))


def lambda_handler(event, context):
    client = boto3.client('logs')
    response = client.create_export_task(
         logGroupName=GROUP_NAME,
         fromTime=fromDate,
         to=toDate,
         destination=DESTINATION_BUCKET,
         destinationPrefix=BUCKET_PREFIX
        )
    print(response)


# import boto3
# import os
# import json

# def handler(event, context):
#     s3_bucket_name = os.environ["S3_BUCKET_NAME"]
#     log_group_name = os.environ["LOG_GROUP_NAME"]
#     log_stream_name = os.environ["LOG_STREAM_NAME"]

#     logs_client = boto3.client("logs")
#     #s3_client = boto3.client("s3")

#     response = logs_client.get_log_events(
#         logGroupName=log_group_name,
#         logStreamName=log_stream_name,
#         limit=100,  # Adjust as needed
#         startFromHead=True,
#     )

#     log_events = response.get("events", [])

#     if log_events:
#         # Convert log events to JSON and upload to S3
#         log_data = [json.dumps(log_event) for log_event in log_events]
#         s3_client.put_object(
#             Bucket=s3_bucket_name,
#             Key=f"logs/{log_group_name}/{log_stream_name}/{context.aws_request_id}.json",
#             Body="\n".join(log_data),
#         )

#     return {"statusCode": 200, "body": "Logs sent to S3 successfully"}

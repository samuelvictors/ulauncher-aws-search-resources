import urllib.parse
from abc import ABC, abstractmethod
from enum import Enum


class AwsResourceName(Enum):
  FUNCTION = "function"
  TABLE = "table"
  BUCKET = "bucket"
  LOG = "log"

  @classmethod
  def from_value(cls, value):
    for resource_name in cls:
      if resource_name.value == value:
        return resource_name
    return None

class AwsResourceType(ABC):
  DEFAULT_REGION = "sa-east-1"

  def __init__(self, name, icon):
    self.name = name
    self.icon = icon

  @abstractmethod
  def search_resources(self, command_runner, profile_info):
    pass

  @abstractmethod
  def get_url(self, resource_identification):
    pass

  @classmethod
  def encode_name(cls, resource_name):
    return urllib.parse.quote(resource_name, safe="")

class LambdaFunction(AwsResourceType):
  def __init__(self):
    super().__init__(AwsResourceName.FUNCTION.value, "images/lambda.png")

  def search_resources(self, command_runner, profile_info):
    return command_runner("aws lambda list-functions --query 'Functions[].FunctionArn'")

  def get_url(self, resource_arn):
    arn_elements = resource_arn.split(":")
    is_resource_name = len(arn_elements) == 1
    region = resource_arn.split(":")[3] if not is_resource_name else self.DEFAULT_REGION
    function_name = resource_arn.split(":")[6] if not is_resource_name else resource_arn
    return "https://{}.console.aws.amazon.com/lambda/home#/functions/{}?tab=code".format(region, AwsResourceType.encode_name(function_name))

class DynamoTable(AwsResourceType):
  def __init__(self):
    super().__init__(AwsResourceName.TABLE.value, "images/dynamo.png")

  def search_resources(self, command_runner, profile_info):
    table_names = command_runner("aws dynamodb list-tables --query 'TableNames[]'")
    return list(map(lambda t: f"arn:aws:dynamodb:{profile_info.region}:{profile_info.account_id}:table/{t}", table_names))
  

  def get_url(self, resource_arn):
    arn_elements = resource_arn.split(":")
    is_resource_name = len(arn_elements) == 1
    region = resource_arn.split(":")[3] if not is_resource_name else self.DEFAULT_REGION
    table_name_section = resource_arn.split(":")[5] if not is_resource_name else None
    table_name = table_name_section.split("/")[1] if table_name_section else resource_arn
    return "https://{}.console.aws.amazon.com/dynamodbv2/home#item-explorer?maximize=true&table={}".format(region, AwsResourceType.encode_name(table_name))

class S3Bucket(AwsResourceType):
  def __init__(self):
    super().__init__(AwsResourceName.BUCKET.value, "images/bucket.png")

  def search_resources(self, command_runner, profile_info):
    return command_runner("aws s3api list-buckets --query 'Buckets[*].Name'")

  def get_url(self, bucket_name):
    return "https://s3.console.aws.amazon.com/s3/buckets/{}?tab=objects".format(AwsResourceType.encode_name(bucket_name))
  
class CloudWatchLog(AwsResourceType):
  def __init__(self):
    super().__init__(AwsResourceName.LOG.value, "images/cloudwatch.png")

  def search_resources(self, command_runner, profile_info):
    return command_runner("aws logs describe-log-groups --query 'logGroups[].arn'")

  def get_url(self, resource_arn):
    arn_elements = resource_arn.split(":")
    is_resource_name = len(arn_elements) == 1
    region = resource_arn.split(":")[3] if not is_resource_name else self.DEFAULT_REGION
    log_group_name = resource_arn.split(":")[6] if not is_resource_name else resource_arn
    return "https://{}.console.aws.amazon.com/cloudwatch/home#logsV2:log-groups/log-group/{}".format(region, AwsResourceType.encode_name(log_group_name))

# class AwsResourceType:
#   _URLS = {
#     AwsResourceName.FUNCTION: "https://sa-east-1.console.aws.amazon.com/lambda/home?region=sa-east-1#/functions/{}?tab=code",
#     AwsResourceName.TABLE: "https://sa-east-1.console.aws.amazon.com/dynamodbv2/home?region=sa-east-1#item-explorer?initialTagKey=&maximize=true&table={}",
#     AwsResourceName.BUCKET: "https://s3.console.aws.amazon.com/s3/buckets/{}?region=sa-east-1&tab=objects",
#     AwsResourceName.LOG: "https://sa-east-1.console.aws.amazon.com/cloudwatch/home?region=sa-east-1#logsV2:log-groups/log-group/{}"
#   }

#   _SEARCH_COMMANDS = {
#     AwsResourceName.FUNCTION: "aws lambda list-functions --query 'Functions[].FunctionArn'",
#     AwsResourceName.TABLE: "aws dynamodb list-tables --query 'TableNames[]'",
#     AwsResourceName.BUCKET: "aws s3api list-buckets --query 'Buckets[*].Name'",
#     AwsResourceName.LOG: "aws logs describe-log-groups --query 'logGroups[].arn'"
#   }

#   _FETCH_RESOURCE_COMMANDS = {
#     AwsResourceName.TABLE: "aws dynamodb describe-table --table-name {} --query 'Table.TableArn' --output text",
#   }

#   _ICONS = {
#     AwsResourceName.FUNCTION: "images/lambda.png",
#     AwsResourceName.TABLE: "images/dynamo.png",
#     AwsResourceName.BUCKET: "images/bucket.png",
#     AwsResourceName.LOG: "images/cloudwatch.png"
#   }

#   def __init__(self, name, icon, url, search_command):
#     self.name = name
#     self.icon = icon
#     self.url = url
#     self.search_command = search_command

#   @classmethod
#   def from_resource_name(cls, resource_name):
#     return cls(
#       resource_name.value,
#       cls._ICONS[resource_name],
#       cls._URLS[resource_name],
#       cls._SEARCH_COMMANDS[resource_name]
#     )

aws_resource_types = {
  AwsResourceName.FUNCTION: LambdaFunction(),
  AwsResourceName.TABLE: DynamoTable(),
  AwsResourceName.BUCKET: S3Bucket(),
  AwsResourceName.LOG: CloudWatchLog()
}
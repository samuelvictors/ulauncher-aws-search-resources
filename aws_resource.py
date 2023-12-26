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

class AwsResourceType:
  _URLS = {
    AwsResourceName.FUNCTION: "https://sa-east-1.console.aws.amazon.com/lambda/home?region=sa-east-1#/functions/{}?tab=code",
    AwsResourceName.TABLE: "https://sa-east-1.console.aws.amazon.com/dynamodbv2/home?region=sa-east-1#item-explorer?initialTagKey=&maximize=true&table={}",
    AwsResourceName.BUCKET: "https://s3.console.aws.amazon.com/s3/buckets/{}?region=sa-east-1&tab=objects",
    AwsResourceName.LOG: "https://sa-east-1.console.aws.amazon.com/cloudwatch/home?region=sa-east-1#logsV2:log-groups/log-group/{}"
  }

  _COMMANDS = {
    AwsResourceName.FUNCTION: "aws lambda list-functions --query 'Functions[*].FunctionName'",
    AwsResourceName.TABLE: "aws dynamodb list-tables --query 'TableNames[]'",
    AwsResourceName.BUCKET: "aws s3api list-buckets --query 'Buckets[*].Name'",
    AwsResourceName.LOG: "aws logs describe-log-groups --query 'logGroups[*].logGroupName'"
  }

  _ICONS = {
    AwsResourceName.FUNCTION: "images/lambda.png",
    AwsResourceName.TABLE: "images/dynamo.png",
    AwsResourceName.BUCKET: "images/bucket.png",
    AwsResourceName.LOG: "images/cloudwatch.png"
  }

  def __init__(self, name, icon, url, search_command):
    self.name = name
    self.icon = icon
    self.url = url
    self.search_command = search_command

  @classmethod
  def from_resource_name(cls, resource_name):
    return cls(
      resource_name.value,
      cls._ICONS[resource_name],
      cls._URLS[resource_name],
      cls._COMMANDS[resource_name]
    )

aws_resource_types = {}
for resource_name in AwsResourceName:
  aws_resource_types[resource_name] = AwsResourceType.from_resource_name(resource_name)
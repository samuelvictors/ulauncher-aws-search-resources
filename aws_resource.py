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
  def get_identification_components(self, resource_identification):
    pass

  def get_label(self, resource_identification):
    return self.get_identification_components(resource_identification)['resource_name']

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
  
  def get_identification_components(self, resource_arn):
    arn_elements = resource_arn.split(":")
    is_resource_name = len(arn_elements) == 1
    return {
      "region": resource_arn.split(":")[3] if not is_resource_name else self.DEFAULT_REGION,
      "resource_name": resource_arn.split(":")[6] if not is_resource_name else resource_arn,
      "account_id": resource_arn.split(":")[4] if not is_resource_name else ""
    }

  def get_url(self, resource_arn):
    resource_components = self.get_identification_components(resource_arn)
    region = resource_components["region"]
    function_name = resource_components["resource_name"]
    return "https://{}.console.aws.amazon.com/lambda/home#/functions/{}?tab=code".format(region, AwsResourceType.encode_name(function_name))

class DynamoTable(AwsResourceType):
  def __init__(self):
    super().__init__(AwsResourceName.TABLE.value, "images/dynamo.png")

  def search_resources(self, command_runner, profile_info):
    table_names = command_runner("aws dynamodb list-tables --query 'TableNames[]'")
    return list(map(lambda t: f"arn:aws:dynamodb:{profile_info.region}:{profile_info.account_id}:table/{t}", table_names))
  
  def get_identification_components(self, resource_arn):
    arn_elements = resource_arn.split(":")
    is_resource_name = len(arn_elements) == 1
    return {
      "region": resource_arn.split(":")[3] if not is_resource_name else self.DEFAULT_REGION,
      "resource_name": resource_arn.split(":")[5].split('/')[1] if not is_resource_name else resource_arn,
      "account_id": resource_arn.split(":")[4] if not is_resource_name else ""
    }

  def get_url(self, resource_arn):
    resource_components = self.get_identification_components(resource_arn)
    region = resource_components["region"]
    table_name = resource_components["resource_name"]
    return "https://{}.console.aws.amazon.com/dynamodbv2/home#item-explorer?maximize=true&table={}".format(region, AwsResourceType.encode_name(table_name))

class S3Bucket(AwsResourceType):
  def __init__(self):
    super().__init__(AwsResourceName.BUCKET.value, "images/bucket.png")

  def search_resources(self, command_runner, profile_info):
    return command_runner("aws s3api list-buckets --query 'Buckets[*].Name'")

  def get_identification_components(self, bucket_name):
    return { "resource_name": bucket_name }

  def get_url(self, bucket_name):
    return "https://s3.console.aws.amazon.com/s3/buckets/{}?tab=objects".format(AwsResourceType.encode_name(bucket_name))
  
class CloudWatchLog(AwsResourceType):
  def __init__(self):
    super().__init__(AwsResourceName.LOG.value, "images/cloudwatch.png")

  def search_resources(self, command_runner, profile_info):
    return command_runner("aws logs describe-log-groups --query 'logGroups[].arn'")

  def get_identification_components(self, resource_arn):
    arn_elements = resource_arn.split(":")
    is_resource_name = len(arn_elements) == 1
    return {
      "region": resource_arn.split(":")[3] if not is_resource_name else self.DEFAULT_REGION,
      "resource_name": resource_arn.split(":")[6] if not is_resource_name else resource_arn,
      "account_id": resource_arn.split(":")[4] if not is_resource_name else ""
    }
  
  def get_label(self, resource_arn):
    resource_name = self.get_identification_components(resource_arn)['resource_name']
    return resource_name.replace("/aws/lambda/", "")

  def get_url(self, resource_arn):
    resource_components = self.get_identification_components(resource_arn)
    region = resource_components["region"]
    log_group_name = resource_components["resource_name"]
    return "https://{}.console.aws.amazon.com/cloudwatch/home#logsV2:log-groups/log-group/{}".format(region, AwsResourceType.encode_name(log_group_name))

aws_resource_types = {
  AwsResourceName.FUNCTION: LambdaFunction(),
  AwsResourceName.TABLE: DynamoTable(),
  AwsResourceName.BUCKET: S3Bucket(),
  AwsResourceName.LOG: CloudWatchLog()
}

class AwsResourceType:
  def __init__(self, name, icon, url, search_command):
    self.name = name
    self.icon = icon
    self.url = url
    self.search_command = search_command

_function = AwsResourceType(
  name="function",
  icon="images/lambda.png",
  url="https://sa-east-1.console.aws.amazon.com/lambda/home?region=sa-east-1#/functions/{}?tab=code",
  search_command="aws lambda list-functions --query 'Functions[*].FunctionName'"
)

_table = AwsResourceType(
  name="table",
  icon="images/dynamo.png",
  url="https://sa-east-1.console.aws.amazon.com/dynamodbv2/home?region=sa-east-1#item-explorer?initialTagKey=&maximize=true&table={}",
  search_command="aws dynamodb list-tables --query 'TableNames[]'"
)

_bucket = AwsResourceType(
  name="bucket",
  icon="images/bucket.png",
  url="https://s3.console.aws.amazon.com/s3/buckets/{}?region=sa-east-1&tab=objects",
  search_command="aws s3api list-buckets --query 'Buckets[*].Name'"
)

_log = AwsResourceType(
  name="log",
  icon="images/cloudwatch.png",
  url="https://sa-east-1.console.aws.amazon.com/cloudwatch/home?region=sa-east-1#logsV2:log-groups/log-group/{}",
  search_command="aws logs describe-log-groups --query 'logGroups[*].logGroupName'"
)

resource_types = {
  "function": _function,
  "table": _table,
  "bucket": _bucket,
  "log": _log
}
import re


class AwsProfileInfo:
    def __init__(self, profile_name, command_runner):
      self.profile_name = profile_name
      self.region = self._remove_extra_chars(command_runner("aws configure get region --output text", "text"))
      self.account_id = self._remove_extra_chars(command_runner("aws sts get-caller-identity --query 'Account' --output text", "text"))
    
    def _remove_extra_chars(self, string):
      return re.sub(r'[\n"]', "", string)
    
    def to_dict(self):
      return {
        "profile_name": self.profile_name or "default",
        "region": self.region,
        "account_id": self.account_id
      }

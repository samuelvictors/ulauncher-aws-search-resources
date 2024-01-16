import re


class AwsProfileInfo:
    def __init__(self, profile_name, command_runner):
      self.profile_name = profile_name
      self.region = self._remove_extra_chars(command_runner("aws configure get region", "text"))
      self.account_id = self._remove_extra_chars(command_runner("aws sts get-caller-identity --query 'Account'", "text"))
    
    def _remove_extra_chars(self, string):
      return re.sub(r'[\n"]', "", string)
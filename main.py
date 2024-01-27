import json
import os
import subprocess
import sys
import re
from pathlib import Path

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.ExtensionCustomAction import \
    ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import \
    RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.event import ItemEnterEvent, KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from aws_resource import AwsResourceName, aws_resource_types

UPDATE_ICON = "images/update.png"
ENVIRONMENT_ICON = "images/environment.png"
MAX_ITEMS_IN_LIST = 8
LINE_MAX_SIZE = 67
ARGUMENTS_SEPARATOR = r"(?<!\\)," # any comma not preceded by a backslash (which is working as an escape character)
PROFILE_ARGUMENTS_OPERATOR = r"(?<!\\)=" # any equal sign not preceded by a backslash (which is working as an escape character)

class AWSResourceSearch(Extension):
    def __init__(self):
        super(AWSResourceSearch, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener()) 


class KeywordQueryEventListener(EventListener):

    def format_description_into_line_size(self, label):
        words = label.split(" ")
        formatted_label = f"{words[0]}"
        for word in words[1:]:
            next_segment_candidate = f"{formatted_label} {word}"
            last_line = next_segment_candidate.split("\n")[-1]
            formatted_label = next_segment_candidate if len(last_line) <= LINE_MAX_SIZE else f"{formatted_label}\n{word}"
        return formatted_label

    def assemble_resource_description(self, resource_components, command_description):
        if 'account_id' in resource_components:
            return f"{resource_components['region']} / {resource_components['account_id']}\n{command_description}"
        return command_description

    def calculate_resource_original_profile(self, resource_components, resource_type, profiles_info, fallback_resources_origin):
        if resource_type.name == AwsResourceName.BUCKET.value:
            resource_name = resource_components["resource_name"]
            return fallback_resources_origin.get(resource_name, None)
        else:
            resource_account_id = resource_components.get("account_id", None)
            resource_region = resource_components.get("region", None)
            if not resource_account_id:
                return None
            for profile_info in profiles_info:
                if profile_info['account_id'] == resource_account_id and profile_info['region'] == resource_region:
                    return profile_info['profile_name']
            return None

    def format_command(self, browser, url, arguments):
        unescaped_arguments = arguments.replace("\\,", ",").replace("\\=", "=")
        if not "%url" in unescaped_arguments:
            return f"{browser} {unescaped_arguments} {url}"
        return f"{browser} {unescaped_arguments.replace('%url', url)}"

    def calculate_command(self, resource_components, resource_type, url, browser, arguments, profiles_info, fallback_resources_origin):
        default_command = f"{browser} {url}"
        if not arguments:
            return default_command
        argument_options = re.split(ARGUMENTS_SEPARATOR, arguments)
        if not re.search(PROFILE_ARGUMENTS_OPERATOR, argument_options[0]): # "arguments" preference is not specifying an AWS profile; applying to all resources
            return self.format_command(browser, url, argument_options[0])
        original_profile = self.calculate_resource_original_profile(resource_components, resource_type, profiles_info, fallback_resources_origin)
        if not original_profile:
            return default_command
        for argument_option in argument_options:
            match = re.search(PROFILE_ARGUMENTS_OPERATOR, argument_option)
            if match:
                profile, arguments_value = re.split(PROFILE_ARGUMENTS_OPERATOR, argument_option)
                if profile == original_profile:
                    return self.format_command(browser, url, arguments_value)
        return default_command

    def on_event(self, event, extension):
        with open(Path(__file__).with_name('resources.json'), "r") as f:
            aws_resources_file = json.load(f)
        with open(Path(__file__).with_name("profiles_info.json"), "r") as f:
            profiles_info = json.load(f)
        with open(Path(__file__).with_name("fallback_resources_origin.json"), "r") as f:
            fallback_resources_origin = json.load(f)

        items = []
        query = event.get_argument() or ""
        keyword = event.get_keyword()
        browser = extension.preferences['browser']

        for kwId, kw in extension.preferences.items():
            if kw == keyword:
                keyword_id = kwId

        if (keyword_id == 'update'):
            profile_preference = extension.preferences.get('profile', None)
            stage_preference = extension.preferences.get('stages', None)
            full_update_description = f"Press enter to update resources with {profile_preference.replace(',', ', ') or 'default'} profile(s)"
            formatted_update_description = self.format_description_into_line_size(full_update_description)
            update_data = {'profiles': profile_preference} if profile_preference else {}
            if stage_preference:
                update_data['stages'] = stage_preference
            return RenderResultListAction([ExtensionResultItem(icon=UPDATE_ICON,
                                                               name="Update AWS Resources",
                                                               description=formatted_update_description,
                                                               on_enter=ExtensionCustomAction(data=update_data, keep_app_open=True))])
        
        resource_type = aws_resource_types[AwsResourceName.from_value(keyword_id)]
        search_terms = query.lower().strip().split(" ")
        target_environment = search_terms[0]
        environments = [*aws_resources_file[resource_type.name].keys()]

        if not query.strip():
            return RenderResultListAction([ExtensionResultItem(icon=ENVIRONMENT_ICON,
                                                               name="Type an environment",
                                                               description="Example: 'beta'",
                                                               on_enter=DoNothingAction())])

        if (len(search_terms) == 1):
            if (target_environment in environments):
                return RenderResultListAction([ExtensionResultItem(icon=resource_type.icon,
                                                                   name=f"Type a {resource_type.name}",
                                                                   description="Example: 'marketplace",
                                                                   on_enter=DoNothingAction())])
            for environment in environments:
                if (target_environment in environment.lower()):
                    items.append(ExtensionResultItem(icon=ENVIRONMENT_ICON,
                                                     name=environment,
                                                     description="Press <enter> to select this environment",
                                                     on_enter=SetUserQueryAction(f"{keyword} {environment} ")))
                if (len(items) >= MAX_ITEMS_IN_LIST):
                    return RenderResultListAction(items)

        elif (len(search_terms) > 1):
            for aws_resource_arn in aws_resources_file[resource_type.name][target_environment]:
                if all(term.lower() in aws_resource_arn.lower() for term in search_terms):
                    url = resource_type.get_url(aws_resource_arn)
                    resource_components = resource_type.get_identification_components(aws_resource_arn)
                    command_description = f"Press <enter> to open in {browser}"
                    command = self.calculate_command(resource_components, 
                                                     resource_type, 
                                                     url, 
                                                     browser, 
                                                     extension.preferences.get('arguments', None),
                                                     profiles_info,
                                                     fallback_resources_origin)
                    items.append(ExtensionResultItem(icon=resource_type.icon,
                                                     name=resource_type.get_label(aws_resource_arn),
                                                     description=self.assemble_resource_description(resource_components, command_description),
                                                     on_enter=RunScriptAction(command)))
                if (len(items) >= MAX_ITEMS_IN_LIST):
                    return RenderResultListAction(items)

        if not items:
            return RenderResultListAction([ExtensionResultItem(icon=resource_type.icon if len(search_terms) > 1 else ENVIRONMENT_ICON,
                                                               name="{} not found".format("Resource" if len(
                                                                   search_terms) > 1 else "Environment"),
                                                               description="Try a different query",
                                                               on_enter=HideWindowAction())])

        return RenderResultListAction(items)

class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):
        data = event.get_data()
        script_path = os.path.join(os.path.dirname(__file__), "update.py")
        python_executable = sys.executable
        update_command_args = [python_executable, script_path, data.get('profiles', ''), data.get('stages', 'dev,beta,prod')]
        subprocess.run(update_command_args)
        return RenderResultListAction([ExtensionResultItem(icon=UPDATE_ICON,
                                                        name="Update done",
                                                        on_enter=HideWindowAction())])


if __name__ == '__main__':
    AWSResourceSearch().run()

import json
import os
import subprocess
import sys
import urllib.parse
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

UPDATE_ICON = "images/update.png"
ENVIRONMENT_ICON = "images/environment.png"
RESOURCE_ICON = {
    'bucket': "images/bucket.png",
    'function': "images/lambda.png",
    'table': "images/dynamo.png",
    'log': "images/cloudwatch.png"
}
RESOURCE_URL = {
    'bucket': "https://s3.console.aws.amazon.com/s3/buckets/{}?region=sa-east-1&tab=objects",
    'function': "https://sa-east-1.console.aws.amazon.com/lambda/home?region=sa-east-1#/functions/{}?tab=code",
    'table': "https://sa-east-1.console.aws.amazon.com/dynamodbv2/home?region=sa-east-1#item-explorer?initialTagKey=&maximize=true&table={}",
    'log': "https://sa-east-1.console.aws.amazon.com/cloudwatch/home?region=sa-east-1#logsV2:log-groups/log-group/{}"
}
MAX_ITEMS_IN_LIST = 8


class AWSResourceSearch(Extension):
    def __init__(self):
        super(AWSResourceSearch, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener()) 


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        with open(Path(__file__).with_name('resources.json'), "r") as f:
            aws_resources = json.load(f)

        items = []
        query = event.get_argument() or ""
        keyword = event.get_keyword()
        browser = extension.preferences['browser']

        for kwId, kw in extension.preferences.items():
            if kw == keyword:
                keyword_id = kwId

        if (keyword_id == 'update'):
            profile_preference = extension.preferences.get('profile', None)
            update_description = f"Press enter to update resources with {profile_preference or 'default'} profile"
            update_data = {'profile': profile_preference} if profile_preference else {}
            return RenderResultListAction([ExtensionResultItem(icon=UPDATE_ICON,
                                                               name="Update AWS Resources",
                                                               description=update_description,
                                                               on_enter=ExtensionCustomAction(data=update_data, keep_app_open=True))])
        
        search_terms = query.lower().strip().split(" ")
        target_environment = search_terms[0]
        environments = [*aws_resources[keyword_id].keys()]

        if not query.strip():
            return RenderResultListAction([ExtensionResultItem(icon=ENVIRONMENT_ICON,
                                                               name="Type an environment",
                                                               description="Example: 'beta'",
                                                               on_enter=DoNothingAction())])

        if (len(search_terms) == 1):
            if (target_environment in environments):
                return RenderResultListAction([ExtensionResultItem(icon=RESOURCE_ICON[keyword_id],
                                                                   name=f"Type a {keyword_id}",
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
            for aws_resource_name in aws_resources[keyword_id][target_environment]:
                if all(term.lower() in aws_resource_name.lower() for term in search_terms):
                    url = RESOURCE_URL[keyword_id].format(
                        urllib.parse.quote(aws_resource_name, safe=""))
                    items.append(ExtensionResultItem(icon=RESOURCE_ICON[keyword_id],
                                                     name=aws_resource_name,
                                                     description=f"Press <enter> to open in {browser}",
                                                     on_enter=RunScriptAction(f"{browser} '{url}'")))
                if (len(items) >= MAX_ITEMS_IN_LIST):
                    return RenderResultListAction(items)

        if not items:
            return RenderResultListAction([ExtensionResultItem(icon=RESOURCE_ICON[keyword_id] if len(search_terms) > 1 else ENVIRONMENT_ICON,
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
        update_command_args = [python_executable, script_path]
        if ('profile' in data):
            update_command_args.append(data['profile'])
        subprocess.run(update_command_args)
        return RenderResultListAction([ExtensionResultItem(icon=UPDATE_ICON,
                                                        name="Update done",
                                                        on_enter=HideWindowAction())])


if __name__ == '__main__':
    AWSResourceSearch().run()
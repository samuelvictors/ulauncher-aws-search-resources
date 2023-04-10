import json
import urllib.parse
from pathlib import Path

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction

ENVIRONMENT_ICON = "images/environment.png"
RESOURCE_ICON = {
    'bucket': "images/bucket.png",
    'function': "images/lambda.png",
    'table': "images/dynamo.png"
}
RESOURCE_URL = {
    'bucket': "https://s3.console.aws.amazon.com/s3/buckets/{}?region=sa-east-1&tab=objects",
    'function': "https://sa-east-1.console.aws.amazon.com/lambda/home?region=sa-east-1#/functions/{}?tab=code",
    'table': "https://sa-east-1.console.aws.amazon.com/dynamodbv2/home?region=sa-east-1#item-explorer?initialTagKey=&maximize=true&table={}"
}
MAX_ITEMS_IN_LIST = 8


class AWSResourceSearch(Extension):
    def __init__(self):
        super(AWSResourceSearch, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        with open(Path(__file__).with_name('resources.json'), "r") as f:
            aws_resources = json.load(f)

        items = []
        query = event.get_argument() or ""
        keyword = event.get_keyword()

        for kwId, kw in extension.preferences.items():
            if kw == keyword:
                keyword_id = kwId

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
                        urllib.parse.quote(aws_resource_name))
                    items.append(ExtensionResultItem(icon=RESOURCE_ICON[keyword_id],
                                                     name=aws_resource_name,
                                                     description="Press <enter> to open in browser",
                                                     on_enter=RunScriptAction("xdg-open '%s'" % url)))
                if (len(items) >= MAX_ITEMS_IN_LIST):
                    return RenderResultListAction(items)

        if not items:
            return RenderResultListAction([ExtensionResultItem(icon=RESOURCE_ICON[keyword_id] if len(search_terms) > 1 else ENVIRONMENT_ICON,
                                                               name="{} not found".format("Resource" if len(
                                                                   search_terms) > 1 else "Environment"),
                                                               description="Try a different query",
                                                               on_enter=HideWindowAction())])

        return RenderResultListAction(items)


if __name__ == '__main__':
    AWSResourceSearch().run()

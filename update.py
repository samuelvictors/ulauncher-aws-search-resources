#!/usr/bin/python

import re
import gi
import json
import sys
import subprocess
import threading

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

# AWS resources to update
resourceList = [
    {
        "name": "bucket",
        "command": "aws s3api list-buckets --query 'Buckets[*].Name'"
    },
    {
        "name": "function",
        "command": "aws lambda list-functions --query 'Functions[*].FunctionName'",
    },
    {
        "name": "table",
        "command": "aws dynamodb list-tables --query 'TableNames[]'"
    },
]
profile = sys.argv[1]


def process_resource(resource_item, resources_label):
    try:
        resources_label.set_text(f"Updating {resource_item['name']}...")
        resources = json.load(open("resources.json"))
        resource_name_list = get_aws_resource(resource_item["command"])
        resources[resource_item["name"]] = {}
        for resource_name in resource_name_list:
            match = re.search(r"-(beta|sdbx|prod|dvdv\w+)", resource_name)
            if match:
                env = match.group(1)
                if env not in resources[resource_item["name"]]:
                    resources[resource_item["name"]][env] = []
                resources[resource_item["name"]][env].append(resource_name)
        json.dump(resources, open("resources.json", "w"), indent=2)
    except Exception:
        resources_label.set_markup(
            f"<span color='red'>Error: An error occurred while updating {resource_item['name']}.</span>")


def update_resources(resources_label, window):
    change_aws_credentials()
    for resource_item in resourceList:
        process_resource(resource_item, resources_label)
    window.destroy()
    Gtk.main_quit()


def get_aws_resource(command):
    return json.loads(subprocess.check_output(command, shell=True))


def update_progress(progress_bar):
    if progress_bar.get_fraction() < 1:
        progress_bar.pulse()
        return True
    else:
        return False


def create_window():
    window = Gtk.Window()
    window.set_title("AWS Resources Update")
    window.set_position(Gtk.WindowPosition.CENTER)
    window.connect("destroy", Gtk.main_quit)
    window.set_border_width(10)

    vbox = Gtk.VBox(spacing=10)
    window.add(vbox)

    resource_label = Gtk.Label(label="Updating AWS resources...")
    vbox.pack_start(resource_label, True, True, 8)

    progress_bar = Gtk.ProgressBar()
    vbox.pack_start(progress_bar, True, True, 8)

    info_label = Gtk.Label(
        label="This update may take several minutes. Please be patient.")
    vbox.pack_start(info_label, True, True, 8)

    GLib.timeout_add(100, update_progress, progress_bar)

    thread = threading.Thread(target=update_resources, args=(resource_label, window))
    thread.start()

    window.show_all()
    Gtk.main()


def change_aws_credentials():
    if len(sys.argv) > 2:
        subprocess.check_output(f"export AWS_PROFILE={profile}", shell=True)

create_window()

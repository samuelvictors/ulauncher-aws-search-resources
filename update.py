#!/usr/bin/python

import json
import os
import re
import subprocess
import sys
import threading

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

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


def process_resource(resource_item, resources_label, profile):
    try:
        label_text = f"Updating {resource_item['name']}..."
        GLib.idle_add(resources_label.set_text, label_text)
        resources_file_path = os.path.join(os.path.dirname(__file__), "resources.json")
        resources = json.load(open(resources_file_path))
        search_command = f'{resource_item["command"]}{f" --profile={profile}" if profile else ""}'        
        resource_name_list = get_aws_resource(search_command)
        resources[resource_item["name"]] = {}
        for resource_name in resource_name_list:
            match = re.search(r"-(beta|prod)", resource_name)
            if match:
                env = match.group(1)
                if env not in resources[resource_item["name"]]:
                    resources[resource_item["name"]][env] = []
                resources[resource_item["name"]][env].append(resource_name)
        json.dump(resources, open(resources_file_path, "w"), indent=2)
    except Exception:
        error_text = f"<span color='red'>Error: An error occurred while updating {resource_item['name']}.</span>"
        GLib.idle_add(resources_label.set_markup, error_text)


def update_resources(resources_label, window, profile):
    for resource_item in resourceList:
        process_resource(resource_item, resources_label, profile)
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
    window.set_default_size(300, 150)

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vbox.set_margin_start(10)
    vbox.set_margin_end(10)
    window.add(vbox)

    resource_label = Gtk.Label(label="Updating AWS resources...")
    vbox.pack_start(resource_label, True, True, 2)

    profile = next(iter(sys.argv[1:]), None)    
    profile_label = Gtk.Label(label=f"({profile or 'default'} profile)")
    vbox.pack_start(profile_label, True, True, 0)

    progress_bar = Gtk.ProgressBar()
    vbox.pack_start(progress_bar, True, True, 8)

    info_label = Gtk.Label(
        label="This update may take several minutes. Please be patient.")
    vbox.pack_start(info_label, True, True, 8)

    GLib.timeout_add_seconds(1, update_progress, progress_bar)

    process_args = [resource_label, window, profile]
    thread = threading.Thread(target=update_resources, args=process_args)
    thread.start()

    window.show_all()
    Gtk.main()

create_window()

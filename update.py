#!/usr/bin/python

import json
import os
import re
import subprocess
import sys
import threading
import time

import gi

from aws_resource import aws_resource_types

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk


def get_aws_resource(command):
    return json.loads(subprocess.check_output(command, shell=True))

def print_aws_resource_fetch_error(resource_type, error_type, error_value, error_traceback):
    print(f"Error during fetch aws resource {resource_type.name}: {error_type}, {error_value}")
    print(error_traceback)

def process_resource(resource_type, resources_label, profile, stages_regex):
    try:
        label_text = f"Updating {resource_type.name}..."
        GLib.idle_add(resources_label.set_text, label_text)
        resources_file_path = os.path.join(os.path.dirname(__file__), "resources.json")
        resources = json.load(open(resources_file_path))
        search_command = f'{resource_type.search_command}{f" --profile={profile}" if profile else ""}'        
        resource_name_list = get_aws_resource(search_command)
        resources[resource_type.name] = {}
        for resource_name in resource_name_list:
            match = re.search(stages_regex, resource_name)
            if match:
                env = match.group(1)
                if env not in resources[resource_type.name]:
                    resources[resource_type.name][env] = []
                resources[resource_type.name][env].append(resource_name)
        json.dump(resources, open(resources_file_path, "w"), indent=2)
    except:
        error_type, error_value, error_traceback = sys.exc_info()
        print_aws_resource_fetch_error(resource_type, error_type, error_value, error_traceback)
        error_text = f"<span color='red'>Error: An error occurred while updating {resource_type.name}</span>"
        GLib.idle_add(resources_label.set_markup, error_text)
        time.sleep(10)


def update_resources(resources_label, profile, stages_regex):
    for resource_type in aws_resource_types.values():
        process_resource(resource_type, resources_label, profile, stages_regex)
    Gtk.main_quit()

def update_progress(progress_bar):
    if progress_bar.get_fraction() < 1:
        progress_bar.pulse()
        return True
    else:
        return False

def remove_hover_effect(widget):
    style_context = widget.get_style_context()
    style_context.add_class("nohover")

    css_provider = Gtk.CssProvider()
    css_properties = """
    .nohover:hover {
        background-color: initial;
    }
    """
    css_provider.load_from_data(css_properties.encode())
    style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

def add_parameter_label(listbox_container, label_text):
    label_row = Gtk.ListBoxRow()
    remove_hover_effect(label_row)
    label = Gtk.Label(label=label_text)
    label.set_halign(Gtk.Align.START)
    label_row.add(label)
    listbox_container.add(label_row)

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

    listbox = Gtk.ListBox()
    listbox.set_selection_mode(Gtk.SelectionMode.NONE)
    vbox.pack_start(listbox, True, True, 2)

    profile = next(iter(sys.argv[1:]), None)    
    profile = profile if (profile is not None and profile != '') else None
    add_parameter_label(listbox, f"profile: {profile or 'default'}")

    stages = next(iter(sys.argv[2:]), "dev,beta,prod")
    stages_regex = re.compile(f"-({stages.replace(',', '|')})")
    add_parameter_label(listbox, f"stages: {stages}")

    print(f'Update process args: profile={profile} / stages={stages}')

    progress_bar = Gtk.ProgressBar()
    vbox.pack_start(progress_bar, True, True, 8)

    info_label = Gtk.Label(
        label="This update may take several minutes. Please be patient.")
    vbox.pack_start(info_label, True, True, 8)

    GLib.timeout_add_seconds(1, update_progress, progress_bar)

    process_args = [resource_label, profile, stages_regex]
    thread = threading.Thread(target=update_resources, args=process_args)
    thread.start()

    window.show_all()
    Gtk.main()

create_window()

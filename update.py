#!/usr/bin/python

import json
import os
import re
import subprocess
import sys
import threading
import time

import gi

from aws_profile import AwsProfileInfo
from aws_resource import aws_resource_types

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk


def command_runner(additional_args):
    def run_command(command, output_format="json"):
        result = subprocess.check_output(f"{command} {additional_args or ''}", shell=True)
        return json.loads(result) if output_format == "json" else result.decode()
    return run_command

def print_aws_resource_fetch_error(resource_type, error_type, error_value, error_traceback):
    print(f"Error during fetch aws resource {resource_type.name}: {error_type}, {error_value}")
    print(error_traceback)

def build_profile_args(profile_name):
    return f"--profile={profile_name}" if profile_name else None

def is_match_result(stages_regex):
    def run_match(search_result):
        match = re.search(stages_regex, search_result)
        return match is not None
    return run_match

def process_resource_search(resource_type, resources_label, profiles, stages):
    resources_file_path = os.path.join(os.path.dirname(__file__), "resources.json")
    resources = json.load(open(resources_file_path))
    resources[resource_type.name] = {}
    try:
        for profile_info in profiles:
            label_text = f"Updating {resource_type.name} with {profile_info.profile_name or 'default'}"
            GLib.idle_add(resources_label.set_text, label_text)
            print(f"Starting {resource_type.name} update with {profile_info.profile_name or 'default'} at {time.strftime('%H:%M:%S')}")
            stages_regex = re.compile(f"-({stages.replace(',', '|')})")
            runner = command_runner(build_profile_args(profile_info.profile_name))
            search_results = resource_type.search_resources(runner, profile_info)
            for result_item in search_results:
                match = re.search(stages_regex, result_item)
                if match:
                    env = match.group(1)
                    if env not in resources[resource_type.name]:
                        resources[resource_type.name][env] = []
                    resources[resource_type.name][env].append(result_item)
            json.dump(resources, open(resources_file_path, "w"), indent=2)
    except:
        error_type, error_value, error_traceback = sys.exc_info()
        print_aws_resource_fetch_error(resource_type, error_type, error_value, error_traceback)
        error_text = f"<span color='red'>Error: An error occurred while updating {resource_type.name}</span>"
        GLib.idle_add(resources_label.set_markup, error_text)
        time.sleep(10)

def update_resources(resources_label, profile_names, stages):
    profile_names_array = profile_names.split(',') if profile_names else [None]
    profiles = list(map(lambda p: AwsProfileInfo(p, command_runner(build_profile_args(p))), profile_names_array))
    for resource_type in aws_resource_types.values():
        process_resource_search(resource_type, resources_label, profiles, stages)
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
    label_row.set_selectable(False)
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
    window.set_resizable(False)
    window.set_deletable(False)

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vbox.set_margin_start(10)
    vbox.set_margin_end(10)
    window.add(vbox)

    resource_label = Gtk.Label(label="Updating AWS resources...")
    vbox.pack_start(resource_label, True, True, 5)

    listbox = Gtk.ListBox()
    listbox.set_selection_mode(Gtk.SelectionMode.NONE)
    vbox.pack_start(listbox, True, True, 2)

    profile_names = next(iter(sys.argv[1:]), None)    
    profile_names = profile_names if (profile_names is not None and profile_names != '') else None
    add_parameter_label(listbox, f"profiles: {profile_names or 'default'}")

    stages = next(iter(sys.argv[2:]), "dev,beta,prod")
    add_parameter_label(listbox, f"stages: {stages}")

    print(f'Update process args: profiles={profile_names} / stages={stages}')

    progress_bar = Gtk.ProgressBar()
    vbox.pack_start(progress_bar, True, True, 8)

    info_label = Gtk.Label(
        label="This update may take several minutes. Please be patient.")
    vbox.pack_start(info_label, True, True, 8)

    GLib.timeout_add_seconds(1, update_progress, progress_bar)

    process_args = [resource_label, profile_names, stages]
    thread = threading.Thread(target=update_resources, args=process_args)
    thread.start()

    window.show_all()
    Gtk.main()

create_window()

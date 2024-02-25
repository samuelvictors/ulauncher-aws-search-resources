import json
import os

def assemble_file_path(file_name):
    return os.path.join(os.path.dirname(__file__), file_name)

def open_json_file(file_name):
    file_path = assemble_file_path(file_name)
    return json.load(open(file_path))

def update_json_file(file_name, data):
    file_path = assemble_file_path(file_name)
    json.dump(data, open(file_path, "w"), indent=2)

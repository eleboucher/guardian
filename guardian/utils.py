import json


def save_json_to_file(data, file_name):
    with open(file_name, "w+") as fp:
        fp.write(json.dumps(data))

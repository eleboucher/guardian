import json


def save_json_to_file(data, file_name):
    with open(file_name, "w+") as fp:
        fp.write(json.dumps(data))


def get_internship(projects_users):
    ret = {"finished": ":white_check_mark:", "in_progress": ":clock1:"}
    try:
        project = next(
            project for project in projects_users if project["project"]["id"] == 118
        )
    except StopIteration:
        project = None
    try:
        contract = next(
            project for project in projects_users if project["project"]["id"] == 119
        )
    except StopIteration:
        contract = None

    if (
        project is not None
        and contract is not None
        and contract["status"] == "finished"
    ):
        return ret[project["status"]]
    return ":negative_squared_cross_mark:"

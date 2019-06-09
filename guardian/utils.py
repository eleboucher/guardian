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


def pluralize(str, count, plural=None):
    if count == 1:
        return str
    if plural:
        return plural
    return f"{str}s"


def format_timedelta(timedelta):
    s = timedelta.total_seconds()
    ret = ""
    days, remainder = divmod(s, 86400)
    hours, remainder = divmod(remainder, 3600)
    if days > 7:
        return f"{int(days / 7)} {pluralize('week', int(days / 7))}"
    if days > 0:
        ret += f"{days} {pluralize('day', days)}"
    minutes = remainder / 60
    ret += f"{minutes} {pluralize('minute', minutes)}"
    return ret

import json
from flask import Request
from typing import Any


# parse request body, json data or URL query parameters
def payload_print(req: Request) -> str:
    if req.method == "POST":
        if req.is_json:
            return json.dumps(req.json) + "\n"
        else:
            # MultiDict needs some iteration
            ret = "{"

            for key in req.form.keys():
                ret += '"' + key + '": "' + req.form[key] + '", '

            return ret[:-2] + "}\n" if len(ret) > 2 else "{}"

    elif req.method == "GET":
        # MultiDict needs some iteration
        ret = "{"

        for key in req.args.keys():
            ret += '"' + key + '": "' + req.args[key] + '", '

        return ret[:-2] + "}\n" if len(ret) > 2 else "{}"


def pretty_print(req: Request) -> str:
    ret = str(req.method) + ' ' + str(req.url) + ' ' + str(req.host) + '\n'
    for (header, values) in req.headers:
        ret += "  " + str(header) + ": " + values + '\n'

    if req.method == "POST":
        ret += "Request body:\n"
        ret += "  " + payload_print(req) + '\n'

    elif req.method == "GET":
        ret += "URL Query String:\n"
        ret += "  " + payload_print(req) + '\n'

    return ret


def checkParameters(req: Request, column_and_type: dict[str, str]) -> tuple[dict[str, Any], bool]:
    data = {}
    if req.method == "POST":
        if req.is_json:
            data = req.get_json()
        else:
            data = req.form
    elif req.method == "GET":
        data = req.args

    ret = {}
    parameters_valid = True
    for key in column_and_type:
        if key in data:
            ret[key] = get_data(data, key, column_and_type[key])
        else:
            ret[key] = key + " missing!"
            parameters_valid = False
    return ret, parameters_valid


def get_data(data: dict, column_name: str, data_type: str) -> Any:
    if data_type == "int":
        return int(data[column_name])
    else:
        return data[column_name]


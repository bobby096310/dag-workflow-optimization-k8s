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


def parse_data(req: Request, column_and_type):
    data = {}
    if req.method == "POST":
        if req.is_json:
            data = req.get_json()
        else:
            data = req.form
    elif req.method == "GET":
        data = req.args
    return check_if_list(data, column_and_type)


def check_if_list(data: dict, column_and_type):
    ret = {}
    if type(data) == list:
        ret = []
        parameters_valid = True
        for row in data:
            sub_ret, sub_parameters_valid = check_parameters(row, column_and_type)
            ret.append(sub_ret)
            parameters_valid &= sub_parameters_valid
    elif type(data) == dict:
        ret, parameters_valid = check_parameters(data, column_and_type)
    return ret, parameters_valid


def check_parameters(data: dict, column_and_type) -> Any:
    ret = {}
    parameters_valid = True
    for key in column_and_type:
        if key in data:
            #ret[key] = int(data[key]) if column_and_type[key] == "int" else data[key]
            ret[key] = convert_int(data[key], column_and_type[key])
        else:
            ret[key] = key + " missing!"
            parameters_valid = False
    return ret, parameters_valid
    
def convert_int(data, type_str):
    if type(data) == list:
        return [lambda row: convert_int(row, type_str) for row in data]
    elif type_str == "int":
        return int(data)
    else:
        return data

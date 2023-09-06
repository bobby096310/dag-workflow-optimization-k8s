from pprint import pprint
import sys
import time
import requests
import yaml
import json
from datetime import timedelta

import argo_workflows
from argo_workflows.api import workflow_service_api
from argo_workflows.model.io_argoproj_workflow_v1alpha1_workflow_create_request import (
    IoArgoprojWorkflowV1alpha1WorkflowCreateRequest,
)

configuration = argo_workflows.Configuration(host="https://localhost:30343")
configuration.verify_ssl = False

api_client = argo_workflows.ApiClient(configuration)
api_instance = workflow_service_api.WorkflowServiceApi(api_client)

def get_workflow_all(namespace):
    result = {}
    try:
        api_response = api_instance.list_workflows( namespace=namespace )
        result = api_response.to_dict()
    except Exception as error:
        result = {"error": ("An error occurred:", error)}
    return result

def get_workflow(namespace, workflow_name):
    result = {}
    try:
        api_response = api_instance.get_workflow( namespace=namespace, name=workflow_name )
        result = api_response.to_dict()
    except Exception as error:
        result = {"error": ("An error occurred:", error)}
    return result

def parse_status(status):
    end = status["finished_at"]
    start = status["started_at"]
    E2ELat = end - start
    run_result = status["phase"]
    nodes = status["nodes"]
    steps = {}
    for node in nodes:
        if nodes[node]['display_name'].find("(") < 0:
            step = {"id": node}
            step_end = nodes[node]['finished_at']
            step_start = nodes[node]["started_at"]
            step_E2ELat = step_end - step_start
            step_result = nodes[node]["phase"]
            step["End"] = step_end
            step["Start"] = step_start
            step["Latency"] = int(step_E2ELat.total_seconds())
            step_name = nodes[node]['display_name'] if nodes[node]['display_name'] != node else "E2E" #.split(":")[0]
            steps[step_name] = step
    sorted_steps = dict(sorted(steps.items(), key=lambda x:x[1]['Start']))
    lat_str = ""
    for sort_step in sorted_steps:
        lat_str = lat_str + (sort_step + " " + str(sorted_steps[sort_step]["Latency"]) + " ")
    lat_detail = {"Start": start, "End": end, "E2E": E2ELat.total_seconds(), "Steps": steps, "Run_Result": run_result, "Latency String": lat_str}
    return lat_detail

def get_wf_latency(namespace, workflow_name):
    result = get_workflow(namespace, workflow_name)
    if "error" in result:
        return(result)
    return parse_status(result['status'])


def get_wf_latency_all(namespace, by_func=None):
    result = get_workflow_all(namespace)
    if "error" in result:
        return(result)
    else:
        items = result["items"]
        latencies = {}
        for item in items:
            name = item['metadata']['name']
            if by_func is None or ((name.find('-') >= 0 and len(name.split('-')) > 1 and name.split('-')[1] == by_func)):
                dag_run = get_workflow(namespace, name)
                latencies[name] = parse_status(dag_run['status'])
        return latencies

def create_workflow(namespace, filename):
    with open(filename, 'r') as file:
        manifest = yaml.safe_load(file)
        api_client = argo_workflows.ApiClient(configuration)
        api_instance = workflow_service_api.WorkflowServiceApi(api_client)
        api_response = api_instance.create_workflow(
            namespace=namespace,
            body=IoArgoprojWorkflowV1alpha1WorkflowCreateRequest(workflow=manifest, _check_type=False),
            _check_return_type=False)
    workflow = api_response.to_dict()
    return(workflow['metadata']['name'])


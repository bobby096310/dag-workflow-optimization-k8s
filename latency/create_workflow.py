from pprint import pprint

import sys
import requests
import yaml
import json

import argo_workflows
from argo_workflows.api import workflow_service_api
from argo_workflows.model.io_argoproj_workflow_v1alpha1_workflow_create_request import (
    IoArgoprojWorkflowV1alpha1WorkflowCreateRequest,
)

configuration = argo_workflows.Configuration(host="https://localhost:2746")
configuration.verify_ssl = False

#resp = requests.get('https://raw.githubusercontent.com/argoproj/argo-workflows/master/examples/hello-world.yaml')
#manifest = yaml.safe_load(resp.text)

def create_workflow(namespace, filename):
    with open(filename, 'r') as file:
        manifest = yaml.safe_load(file)
        api_client = argo_workflows.ApiClient(configuration)
        api_instance = workflow_service_api.WorkflowServiceApi(api_client)
        api_response = api_instance.create_workflow(
            namespace=namespace,
            body=IoArgoprojWorkflowV1alpha1WorkflowCreateRequest(workflow=manifest, _check_type=False),
            _check_return_type=False)
    return(api_response.to_dict())

def main():
    args = sys.argv[1:]
    if(len(args) < 2):
        print("Please enter namespace and file name")
        return

    pprint(create_workflow(args[0], args[1]))
    

if __name__ == "__main__":
    main()

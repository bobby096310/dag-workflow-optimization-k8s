import sys
import json
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from pprint import pprint

config.load_kube_config()

def get_function(func_name):
    # Enter a context with an instance of the API kubernetes.client
    with client.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = client.CustomObjectsApi(api_client)
        group = 'serving.knative.dev' # str | the custom resource's group
        version = 'v1' # str | the custom resource's version
        namespace = 'default'
        plural = 'services' # str | the custom object's plural name. For TPRs this would be lowercase plural kind.
        name = func_name # str | the custom object's name

        try:
            api_response = api_instance.get_namespaced_custom_object(group, version, namespace, plural, name)
            return api_response
        except ApiException as e:
            return ("Exception when calling CustomObjectsApi->get_cluster_custom_object: %s\n" % e)

def patch_function(func_name, body):
    # Enter a context with an instance of the API kubernetes.client
    with client.ApiClient() as api_client:
        # Create an instance of the API class
        api_client.set_default_header('Content-Type', 'application/json-patch+json') # specify the patch json format
        api_instance = client.CustomObjectsApi(api_client)
        group = 'serving.knative.dev' # str | the custom resource's group
        version = 'v1' # str | the custom resource's version
        namespace = 'default'
        plural = 'services' # str | the custom object's plural name. For TPRs this would be lowercase plural kind.
        name = func_name # str | the custom object's name
        body = json.loads(body) # object | The JSON schema of the Resource to patch.
        force = True

        try:
            api_response = api_instance.patch_namespaced_custom_object(group, version, namespace, plural, name, body)
            return api_response
        except ApiException as e:
            return ("Exception when calling CustomObjectsApi->patch_cluster_custom_object: %s\n" % e)

def concurrency_body(concurrency):
    return '[{"op": "replace", "path": "/spec/template/spec/containerConcurrency", "value": ' + str(concurrency) + '}]'
    
def resources_body(request_cpu, limit_cpu):
    spec = ''
    if request_cpu == '-' and limit_cpu == '-':
        spec = ''
    elif request_cpu != '-':
        spec = '\"requests\": {\"cpu\": \"' + str(request_cpu) + '\"}'
    elif limit_cpu != '-':
        spec = '\"limits\": {\"cpu\": \"' + str(limit_cpu)  + '\"}'
    else:
        spec = '\"requests\": {\"cpu\": \"' + str(request_cpu) + '\"}, \"limits\": {\"cpu\": \"' + str(limit_cpu)  + '\"}'
    return '[{"op": "replace", "path": "/spec/template/spec/containers/0/resources", "value": {' + spec + '}}]'
    
def main():
    args = sys.argv[1:]
    if(len(args) < 1):
        pprint("Please enter action:")
        return
    elif (args[0] == "get"):
        if (len(args) < 2):
            pprint("Please enter function name:")
            return
        pprint(get_function(args[1]))
    elif (args[0] == "patch_conc"):
        if (len(args) < 3):
            pprint("Please enter function name, and concurrency:")
            return
        body = concurrency_body(args[2])
        pprint(patch_function(args[1], body))
    elif (args[0] == "patch_cpu"):
        if (len(args) < 4):
            pprint("Please enter function name, and cpu requests and limits:")
            return
        body = resources_body(args[2], args[3])
        pprint(patch_function(args[1], body))
    
if __name__ == "__main__":
    main()

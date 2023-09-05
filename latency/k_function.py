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
    return '[{"op": "replace", "path": "/spec/template/spec/containers/0/resources", "value": {\"requests\": {\"cpu\": \"' + str(request_cpu) + '\"}, \"limits\": {\"cpu\": \"' + str(limit_cpu)  + '\"}}}]' 


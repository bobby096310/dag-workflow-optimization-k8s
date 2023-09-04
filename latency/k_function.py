import sys
import json
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from pprint import pprint

config.load_kube_config()

def get_function(namespace, func_name):
    # Enter a context with an instance of the API kubernetes.client
    with client.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = client.CustomObjectsApi(api_client)
        group = 'serving.knative.dev' # str | the custom resource's group
        version = 'v1' # str | the custom resource's version
        namespace = namespace
        plural = 'services' # str | the custom object's plural name. For TPRs this would be lowercase plural kind.
        name = func_name # str | the custom object's name

        try:
            api_response = api_instance.get_namespaced_custom_object(group, version, namespace, plural, name)
            return api_response
        except ApiException as e:
            return ("Exception when calling CustomObjectsApi->get_cluster_custom_object: %s\n" % e)

def patch_function(namespace, func_name, body):
    # Enter a context with an instance of the API kubernetes.client
    with client.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = client.CustomObjectsApi(api_client)
        group = 'serving.knative.dev' # str | the custom resource's group
        version = 'v1' # str | the custom resource's version
        namespace = namespace
        plural = 'services' # str | the custom object's plural name. For TPRs this would be lowercase plural kind.
        name = func_name # str | the custom object's name
        body = json.loads(body) # object | The JSON schema of the Resource to patch.
        force = True

        try:
            api_response = api_instance.patch_namespaced_custom_object(group, version, namespace, plural, name, body, force=force)
            return api_response
        except ApiException as e:
            return ("Exception when calling CustomObjectsApi->patch_cluster_custom_object: %s\n" % e)

def concurrency_body(concurrency):
    return '{"spec":{"template":{"spec":{"containerConcurrency": '+ str(concurrency) +'}}}}'


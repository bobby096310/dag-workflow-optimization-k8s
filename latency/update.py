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

def get_pods(namespace="default"):
    with client.ApiClient() as api_client:
        api_instance = client.CoreV1Api(api_client)
        try:
            api_response = api_instance.list_namespaced_pod(namespace=namespace)
            pod_list = []
            for pod_entry in api_response.items:
                pod_list.append(pod_entry.metadata.name)
            #print(pod_list)
            return pod_list
        except ApiException as e:
            print("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)

def clear_pods(namespace="default"):
    with client.ApiClient() as api_client:
        api_instance = client.CoreV1Api(api_client)
        try:
            #api_instance.list_namespaced_pod(namespace=namespace)
            pod_list = get_pods()
            for pod in pod_list:
                print(pod)
                api_response = api_instance.delete_namespaced_pod(pod, namespace)
            #api_response = api_instance.delete_collection_namespaced_pod(namespace=namespace, 
            #        body=client.V1DeleteOptions(), grace_period_seconds=0)
                print(api_response)
        except ApiException as e:
            print("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)

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

def update_function(func_name, new_spec):
    body = ''
    if 'concurrency' in new_spec and 'cpu' in new_spec:
        body = concurrency_body(new_spec['concurrency'])[:-1] + ","  + resources_body(new_spec['cpu'][0], new_spec['cpu'][1])[1:]
    elif 'concurrency' in new_spec:
        body = concurrency_body(new_spec['concurrency'])
    elif 'cpu' in new_spec:
        body = resources_body(new_spec['cpu'][0], new_spec['cpu'][1])
    else:
        return "No changes made"
    return patch_function(func_name, body)

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
    elif (args[0] == "clear_pods"):
        pprint(clear_pods())
    elif (args[0] == "get_pods"):
        pprint(get_pods())

if __name__ == "__main__":
    main()

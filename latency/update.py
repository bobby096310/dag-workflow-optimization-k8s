from k_function import *
from argo_utils import *

def update_argo_yaml(filename, spec):
    if 'timeout' in spec:
        with open(filename, 'r') as file:
            manifest = yaml.safe_load(file)
        with open(filename, 'w') as file:
            curl_template = manifest['spec']['templates'][0]
            curl_template['activeDeadlineSeconds'] = str(spec['timeout'])
            yaml.dump(manifest, file)
        return "workflow updated"
    return "No changes made"

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


def update(filename, func_name, new_spec):
    result = []
    result.append(update_function(func_name, new_spec))
    result.append(update_argo_yaml(filename, new_spec))
    return result


def main():
    args = sys.argv[1:]
    if len(args) < 6:
        pprint("Please enter filename, function, parameters (timeout, concurrency, cpu r and l)")
        return
    spec = {}
    filename = args[0]
    function = args[1]
    timeout = args[2]
    concurrency = args[3]
    cpu1 = args[4]
    cpu2 = args[5]
    if timeout != '-':
        spec['timeout'] = timeout 
    if concurrency != '-':
        spec['concurrency'] = concurrency
    if cpu1 != '-' and cpu2 != '-':
        spec['cpu'] = [cpu1, cpu2]
    #pprint(update_function('vi-classify', {"timeout": 90, "concurrency": 10, "cpu_r": ["1200m", "2"]}))
    pprint(update(filename, function, spec))

if __name__ == "__main__":
    main()

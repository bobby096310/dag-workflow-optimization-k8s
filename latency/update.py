from k_function import *
from argo_utils import *

def update_argo_yaml(filename, spec):
    if 'timeout' in spec:
        with open(filename, 'w') as file:
            manifest = yaml.safe_load(file)
            manifest['spec']['templates'][0]['activeDeadlineSeconds'] = str(spec['timeout'])
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
    update_function(func_name, new_spec)
    update_argo_yaml(filename, new_spec)

def main():
    pprint(update_function('vi-classify', {"timeout": 90, "concurrency": 10, "cpu": ["1200m", "2"]}))
    
if __name__ == "__main__":
    main()

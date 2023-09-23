from lat import *
from update import *
from pdf_cdf import *
import random
import string

filenames = {"ml": "../argo/ml.yaml", "video": "../argo/video.yaml"}
workflow_functions = {"ml": ["ml-pca","ml-param-tune","ml-combine"], "video": ["vi-split", "vi-extract", "vi-shuffle", "vi-classify"]}
conc = [0, 1, 2, 5, 10]
cpu = [['-', '-'], ['1', '-'], ['1', '2'], ['1500m', '-'], ['2', '-'], ['2', '3'], ['3', '-']]
timeout = [60, 75, 90, 120, 0]
bundle = {"ml": ["2", "4", "8"], "video": ["15", "5", "3"]}

def create_random_name(n):
    letters = string.ascii_lowercase
    profile_hash = ''.join(random.choice(letters) for i in range(n))
    return profile_hash

def run_workflows(namespace, workflow_name, filename, times, inp, pre_warm, log_file_name):
    results = {}
    for i in range(int(times)):
        #run_name, result = run_workflow(namespace, filename)
        run_name = workflow_name + "-" + create_random_name(5)
        results[run_name] = run_video(inp, pre_warm)
        with open("logs/" + log_file_name, 'a') as file:
            file.write(run_name + " " + results[run_name] + "\n")
        time.sleep(60)
    return results
    
def run(workflow_name, config, times, pre_warm):
    function_index = config[0]
    conc_index = config[1]
    cpu_index = config[2]
    bundle_index = config[3]
    log_file_name = workflow_name + "_" + str(function_index) + "_" + str(conc_index) + "_" + str(cpu_index) + "_" + str(bundle_index) + "_" + ('T' if pre_warm else 'F') + "_" + create_random_name(5) + ".txt"
    filename = filenames[workflow_name]
    spec = {}
    #if timeout_index != '-':
    #    spec['timeout'] = timeout[timeout_index]
    if conc_index != '-':
        spec['concurrency'] = conc[conc_index]
    if cpu_index != '-':
        spec['cpu'] = cpu[cpu_index]
    update(filename, workflow_functions[workflow_name][function_index], spec)
    inp = {"src_name": "00", "DOP": bundle[workflow_name][bundle_index], "detect_prob": 2}
    result = run_workflows('argo-wf', workflow_name, filename, times, inp, pre_warm, log_file_name)
    final = log_file_name[:-4] + " " +  analyze_result(list(result.values()), 7)
    #get_n_latency(list(result.values()), 95)
    return final

def add_dim(li, li2):
    li_o = []
    for l in li:
        for l2 in li2:
            l2_o = l.copy()
            l2_o.append(l2)
            li_o.append(l2_o)
    return li_o

def possible_configs(workflow_name, base):
    configs = [[]]
    configs = add_dim(configs, range(len(workflow_functions[workflow_name])))
    configs = add_dim(configs, range(len(conc)))
    configs = add_dim(configs, range(len(cpu)))
    return configs

def main():
    pprint(run('video', [3, 1, 0, 1], 10, True))
    #pprint(run('video', [3, 1, 0, 1], 10, False))
    #pprint(run('video', [3, 1, 0, 2], 10, True))
    pprint(run('video', [3, 1, 0, 2], 10, False))
    #pprint(run('video', [3, 1, 1, 1], 10, True))
    #pprint(run('video', [3, 1, 1, 1], 10, False))
    #pprint(run('video', [3, 1, 1, 2], 10, True))
    #pprint(run('video', [3, 1, 1, 2], 10, False))
    #pprint(run('video', [3, 1, 2, 1], 10, True))
    #pprint(run('video', [3, 1, 2, 1], 10, False))
    #pprint(run('video', [3, 1, 2, 2], 10, True))
    pprint(run('video', [3, 1, 2, 2], 10, False))
    #pprint(run('video', [3, 1, 2, 1], 10, True))
    #pprint(run('video', [3, 1, 2, 1], 10, False))
    #pprint(run('video', [3, 1, 3, 2], 10, True))
    #pprint(run('video', [3, 1, 3, 2], 10, False))
    #pprint(run('video', [3, 1, 4, 1], 10, True))
    #pprint(run('video', [3, 1, 4, 1], 10, False))
    #pprint(run('video', [3, 1, 4, 2], 10, True))
    #pprint(run('video', [3, 1, 4, 2], 10, False))
    pprint(run('video', [3, 1, 5, 1], 10, True))
    #pprint(run('video', [3, 1, 5, 1], 10, False))
    #pprint(run('video', [3, 1, 5, 2], 10, True))
    #pprint(run('video', [3, 1, 5, 2], 10, False))
    pprint(run('video', [3, 1, 6, 1], 10, True))
    #pprint(run('video', [3, 1, 6, 1], 10, False))
    #pprint(run('video', [3, 1, 6, 2], 10, True))
    #pprint(run('video', [3, 1, 6, 2], 10, False))    

if __name__ == "__main__":
    main()

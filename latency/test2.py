from lat import *
from update import *
from pdf_cdf import *
from collect2 import *
import random
import string

filenames = {"ml": "../argo/ml.yaml", "video": "../argo/video.yaml"}
workflow_functions = {"ml": ["ml-pca","ml-param-tune","ml-combine"], "video": ["vi-split", "vi-extract", "vi-shuffle", "vi-classify"]}
conc = [0, 1, 2, 5, 10]
cpu = [['-', '-'], ['1', '-'], ['1', '2'], ['1500m', '-'], ['2', '-'], ['2', '3'], ['3', '-']]
bundle = {"ml": ["2", "4", "8"], "video": ["30", "15", "5", "3"]}

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
    inp = {"src_name": "0", "DOP": bundle[workflow_name][bundle_index], "detect_prob": 2}
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

#def run_tests():
    #pprint(run('video', [3, 1, 0, 1], 10, True))
    #pprint(run('video', [3, 1, 0, 1], 10, False))
    #pprint(run('video', [3, 1, 0, 2], 10, True))
    #pprint(run('video', [3, 1, 0, 2], 10, False))
    #pprint(run('video', [3, 1, 1, 1], 10, True))
    #pprint(run('video', [3, 1, 1, 1], 10, False))
    #pprint(run('video', [3, 1, 1, 2], 10, True))
    #pprint(run('video', [3, 1, 1, 2], 10, False))
    #pprint(run('video', [3, 1, 2, 1], 10, True))
    #pprint(run('video', [3, 1, 2, 1], 10, False))
    #pprint(run('video', [3, 1, 2, 2], 10, True))
    #pprint(run('video', [3, 1, 2, 2], 10, False))
    #pprint(run('video', [3, 1, 2, 1], 10, True))
    #pprint(run('video', [3, 1, 2, 1], 10, False))
    #pprint(run('video', [3, 1, 3, 2], 10, True))
    #pprint(run('video', [3, 1, 3, 2], 10, False))
    #pprint(run('video', [3, 1, 4, 1], 10, True))
    #pprint(run('video', [3, 1, 4, 1], 10, False))
    #pprint(run('video', [3, 1, 4, 2], 10, True))
    #pprint(run('video', [3, 1, 4, 2], 10, False))
    #pprint(run('video', [3, 1, 5, 1], 10, True))
    #pprint(run('video', [3, 1, 5, 1], 10, False))
    #pprint(run('video', [3, 1, 5, 2], 10, True))
    #pprint(run('video', [3, 1, 5, 2], 10, False))
    #pprint(run('video', [3, 1, 6, 1], 10, True))
    #pprint(run('video', [3, 1, 6, 1], 10, False))
    #pprint(run('video', [3, 1, 6, 2], 10, True))
    #pprint(run('video', [3, 1, 6, 2], 10, False)) 

def init(workflow_name, func_index, conc, resources, bundling):
    current_list = [r.split(" ")[0] for r in get_P50()]
    for r in range(len(resources)):
        for b in range(len(bundling)):
            entry = workflow_name + "_" + str(func_index) + "_" + str(conc) + "_" + str(r) + "_" + str(b) +  "_F"
            if entry not in current_list:
                print("run " + entry)
                run(workflow_name, [func_index, 1, r, b], 1, False)
                time.sleep(60)

def run_level(configs, level, interval):
    target = (level + 1) * interval
    s = round(len(configs)/pow(2, level))
    config_for_level = configs[:s]
    for config in config_for_level:
        times = int(config.split(" ")[-1])
        if times < target:		
            run_times(config, target - times)
        else:
            print("target met")
            continue

def run_times(input_str, times):
    config_str = input_str.split(" ")[0]
    config_list = config_str.split("_")
    workflow_name = config_list[0]
    #config = config_list[1:5]
    run(workflow_name, [int(config_list[1]), int(config_list[2]), int(config_list[3]), int(config_list[4])], times, False)
   
def get_P50():
    groupnames = fetch_groups()
    agg_list = get_agg_list(groupnames)
    agg_p50 = sort_by_p50(agg_list)
    return agg_p50

def main():
    #args = sys.argv[1:]
    #interval = int(args[0])
    workflow_name = 'video'
    func_index = 3
    conc = 1
    #init(workflow_name, func_index, conc, cpu, bundle[workflow_name])
    configs = get_P50()
    print(configs)
    run_level(configs, 0, 10)
    run_level(configs, 1, 10)
    run_level(configs, 2, 10)
    run_level(configs, 3, 10)
    run_level(configs, 4, 10)
    run_level(configs, 5, 10)

if __name__ == "__main__":
    main()

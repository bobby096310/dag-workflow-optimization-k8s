from runner import run_video, run_ml
from update import update_function
from pdf_cdf import analyze_result
from collect import *
import time
import random
import string

filenames = {"ml": "../argo/ml.yaml", "video": "../argo/video.yaml"}
workflow_functions = {"ml": ["ml-pca","ml-param-tune","ml-combine"], "video": ["vi-split", "vi-extract", "vi-shuffle", "vi-classify"]}
conc = [0, 1, 2, 5, 10]
#cpu = [['-', '-'], ['1', '-'], ['1', '2'], ['1500m', '-'], ['2', '-'], ['2', '3'], ['3', '-']]
cpu = [['-', '-'], ['500m', '500m'], ['1', '1'], ['1500m', '1500m'], ['2', '2'], ['2500m', '2500m'], ['3', '3']]
bundle = {"ml": ["2", "4", "8"], "video": ["30", "15", "5", "3"]}

def create_random_name(n):
    letters = string.ascii_lowercase
    profile_hash = ''.join(random.choice(letters) for i in range(n))
    return profile_hash

# Call the runner to run the workflow based on name
def run_workflows(namespace, workflow_name, filename, times, inp, pre_warm, log_file_name):
    results = {}
    for i in range(int(times)):
        run_name = workflow_name + "-" + create_random_name(5)
        if workflow_name == "video":
            results[run_name] = run_video(inp, pre_warm)
        elif workflow_name == 'ml':
            results[run_name] = run_ml(inp, pre_warm)
        else:
            return "Workflow not found!"
        with open("logs/" + log_file_name, 'a') as file:
            file.write(run_name + " " + results[run_name] + "\n")
        time.sleep(60)
    return results

# Update the spec and run workflows    
def update_and_run(workflow_name, config, times, pre_warm):
    function_index = int(config[0])
    conc_index = config[1]
    cpu_index = config[2]
    bundle_index = int(config[3])
    log_file_name = workflow_name + "_" + str(function_index) + "_" + str(conc_index) + "_" + str(cpu_index) + "_" + str(bundle_index) + "_" + ('T' if pre_warm else 'F') + "_" + create_random_name(5) + ".txt"
    filename = filenames[workflow_name]
    spec = {}
    if conc_index != '-':
        spec['concurrency'] = conc[int(conc_index)]
    if cpu_index != '-':
        spec['cpu'] = cpu[int(cpu_index)]
    update_function(workflow_functions[workflow_name][function_index], spec)
    inp = {"src_name": "0", "DOP": bundle[workflow_name][bundle_index], "detect_prob": 2}
    result = run_workflows('argo-wf', workflow_name, filename, times, inp, pre_warm, log_file_name)
    final = log_file_name[:-4] + " " +  analyze_result(list(result.values()), 7)
    #get_n_latency(list(result.values()), 95)
    return final

#def run_tests():
    #pprint(run('video', [3, 1, 0, 1], 10, True))
    #pprint(run('video', [3, 1, 0, 1], 10, False))

# Run each possible spec once
def init(workflow_name, func_index, conc, resources, bundling):
    current_list = [r.split(" ")[0] for r in get_P50()]
    for r in range(len(resources)):
        for b in range(len(bundling)):
            entry = workflow_name + "_" + str(func_index) + "_" + str(conc) + "_" + str(r) + "_" + str(b) +  "_F"
            if entry not in current_list:
                print("run " + entry)
                update_and_run(workflow_name, [func_index, 1, r, b], 1, False)
                time.sleep(60)

# Run workflows until target is met for the level
def run_level(batch, target):
    for config in batch:
        times = int(config.split(" ")[-1])
        if times < target:		
            run_from_str(config, target - times)
        else:
            print("target met")
            continue

# Run workflow based on input string
def run_from_str(input_str, times):
    config_str = input_str.split(" ")[0]
    config_list = config_str.split("_")
    workflow_name = config_list[0]
    update_and_run(workflow_name, [int(config_list[1]), int(config_list[2]), int(config_list[3]), int(config_list[4])], times, False if config_list[5] == 'F' else True)
    
def get_P50():
    groupnames = fetch_groups()
    agg_list = get_agg_list(groupnames)
    agg_p50 = sort_by_p50(agg_list)
    return agg_p50

def get_next_level(level, interval):
    configs = get_P50()
    target = (level + 1) * interval
    s = round(len(configs)/pow(2, level))
    config_for_level = configs[:s]
    return config_for_level, target
   
def get_best_config():
    groupnames = fetch_groups()
    agg_list = get_agg_list(groupnames)
    agg_p95 = sort_by_p95(agg_list)
    for config in agg_p95:
        if (int(config.split(" ")[-1]) > 99):
            return config
    return "NaN"

def find_best_config(workflow_name, func_index):
    conc = 1
    init(workflow_name, func_index, conc, cpu, bundle[workflow_name])
    level = 0
    while level < 20:
        batch, target = get_next_level(level, 10)
        if len(batch) < 4:
            run_level(batch, 100)
            break
        else:
            run_level(batch, target)
        level += 1
    print(get_best_config())

def run_all(workflow_name, func_index):
    conc = 1
    init(workflow_name, func_index, conc, cpu, bundle[workflow_name])
    batch = get_P50()
    level = 1
    while level < 11:
        print("level: ", level)
        run_level(batch, level * 10)
        level += 1
    print(get_best_config())

def main():
    args = sys.argv[1:]
    #interval = int(args[0])
    code = args[0]
    if code == "best":
        if len(args) < 3:
            print("Please enter workflow name and function index")
        workflow_name = args[1]
        func_index = args[2]
        find_best_config(workflow_name, func_index)
    elif code == "run":
        if len(args) < 8:
            print("Please enter workflow name, function index, concurrency, cpu, bundle, pre_warm, and times")
        workflow_name = args[1]
        func_index = args[2]
        c = args[3]
        r = args[4]
        b = args[5]
        pre_warm = False if args[6] == 'F' else True
        times = args[7]
        update_and_run(workflow_name, [func_index, c, r, b], times, pre_warm)
        #python3 test2.py run video 3 1 - 0 F 10
    elif code == "run_all":
        if len(args) < 3:
            print("Please enter workflow name and function index")
        workflow_name = args[1]
        func_index = args[2]
        run_all(workflow_name, func_index)


if __name__ == "__main__":
    main()

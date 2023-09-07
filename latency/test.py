from update import *
from argo_utils import *
from pdf_cdf import *
import random
import string

filenames = {"ml": "../argo/ml.yaml", "video": "../argo/video.yaml"}
workflow_functions = {"ml": ["ml-pca","ml-param-tune","ml-combine"], "video": ["vi-split", "vi-extract", "vi-shuffle", "vi-classify"]}
timeout = [60, 75, 90, 120]
conc = [0, 1, 2, 5, 10]
cpu = [['100m', '4'], ['500m', '2'], ['1', '2'], ['1', '4'], ['1500m', '4'], ['-', '-'], ['1', '-'], ['1500m', '-']]

def run_workflow(namespace, filename):
    run_name = create_workflow(namespace, filename)
    time.sleep(90)
    result = get_wf_latency(namespace, run_name)
    while "error" in result:
        time.sleep(30)
        result = get_wf_latency(namespace, run_name)
    return run_name, result

def run_workflows(namespace, filename, times, log_file_name):
    results = {}
    for i in range(int(times)):
        run_name, result = run_workflow(namespace, filename)
        if result["Run_Result"] != "Succeeded":
            break
        else:
            results[run_name] = result["Latency String"]
            with open("logs/" + log_file_name, 'a') as file:
                file.write(run_name + " " + results[run_name] + "\n")
        time.sleep(30)
    return results

def run(workflow_name, function_index, timeout_index, conc_index, cpu_index, times):
    letters = string.ascii_lowercase
    profile_hash = ''.join(random.choice(letters) for i in range(5))
    log_file_name = workflow_name + "_" + str(function_index) + "_" + str(timeout_index) + "_" + str(conc_index) + "_" + str(cpu_index) + "_" + profile_hash + ".txt"
    filename = filenames[workflow_name]
    spec = {}
    if timeout_index != '-':
        spec['timeout'] = timeout[timeout_index]
    if conc_index != '-':
        spec['concurrency'] = conc[conc_index]
    if cpu_index != '-':
        spec['cpu'] = cpu[cpu_index]
    update(filename, workflow_functions[workflow_name][function_index], spec)
    result = run_workflows('argo-wf', filename, times, log_file_name)
    final = log_file_name[:-4] + " " +  analyze_result(list(result.values()), 1)
    return final

def main():
    # concurrency
    #pprint(run("video", 3, 3, 0, 0, 5))
    #pprint(run("video", 3, 3, 1, 0, 5))
    #pprint(run("video", 3, 3, 2, 0, 5))
    # timeout
    #pprint(run("video", 3, 1, 2, 0, 5))
    #pprint(run("video", 3, 2, 2, 0, 5))
    #pprint(run("video", 3, 3, 2, 0, 5))
    # cpu
    #pprint(run("video", 3, 2, 2, 0, 5))
    #pprint(run("video", 3, 2, 2, 1, 5))
    #pprint(run("video", 3, 2, 2, 2, 5))
    pprint(run("video", 3, 3, 1, 3, 10))
    pprint(run("video", 3, 3, 1, 6, 10))
    pprint(run("video", 3, 2, 1, 2, 10))
    pprint(run("video", 3, 2, 1, 1, 10))

if __name__ == "__main__":
    main()

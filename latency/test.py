from update import *
from argo_utils import *
from pdf_cdf import *
import random
import string

filenames = {"ml": "../argo/ml.yaml", "video": "../argo/video.yaml"}
workflow_functions = {"ml": ["ml-pca","ml-param-tune","ml-combine"], "video": ["vi-split", "vi-extract", "vi-shuffle", "vi-classify"]}
timeout = [60, 75, 90, 120]
conc = [0, 1, 2, 5, 10]
cpu = [['100m', '4'], ['500m', '2'], ['1', '2']]

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
    log_file_name = workflow_name + "_" + str(timeout_index) + "_" + str(conc_index) + "_" + str(cpu_index) + "_" + profile_hash + ".txt"
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
    final = log_file_name[:-4] + " " +  analyze_result(result)
    with open("logs/logs.txt", 'a') as file:
        file.write(final + "\n")
    return final
    
# [{'dag-video-7cbwp': 'E2E 298.0 split 10.0 extract 21.0 shuffle 10.0 classify 257.0 '}]

def analyze_result(raw_data):
    E2Es = []
    for run in raw_data:
        E2Es.append(float(raw_data[run].split(' ')[1]))
    E2E_mean = round(sum(E2Es) / len(E2Es), 2)
    return "Mean " + str(E2E_mean) + " N95 " +  str(get_n_latency(E2Es, 95)) + " Count " + str(len(E2Es))

def main():
    #pprint(run("video", 3, 3, 1, 0, 1))
    # concurrency
    #pprint(run("video", 3, 3, 1, 0, 5))
    #pprint(run("video", 3, 3, 2, 0, 5))
    #pprint(run("video", 3, 3, 3, 0, 5))
    #pprint(run("video", 3, 3, 4, 0, 5))
    # timeout
    pprint(run("video", 3, 2, 1, 0, 20))
    pprint(run("video", 3, 1, 1, 0, 20))
    pprint(run("video", 3, 3, 1, 0, 20))
    # cpu
    #pprint(run("video", 3, 2, 1, 0, 5))
    #pprint(run("video", 3, 2, 1, 1, 5))
    #pprint(run("video", 3, 2, 1, 2, 5))

if __name__ == "__main__":
    main()

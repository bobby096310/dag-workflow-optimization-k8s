from lat import *
from update import *
from pdf_cdf import *
import random
import string

filenames = {"ml": "../argo/ml.yaml", "video": "../argo/video.yaml"}
workflow_functions = {"ml": ["ml-pca","ml-param-tune","ml-combine"], "video": ["vi-split", "vi-extract", "vi-shuffle", "vi-classify"]}
conc = [0, 1, 2, 5, 10]
cpu = [['-', '-'], ['1', '-'], ['1', '2'], ['1500m', '-']]
timeout = [60, 75, 90, 120, 0]

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
        with open("logs2/" + log_file_name, 'a') as file:
            file.write(run_name + " " + results[run_name] + "\n")
        time.sleep(30)
    return results
    
def run(workflow_name, function_index, conc_index, cpu_index, timeout_index, times, inp, pre_warm):
    log_file_name = workflow_name + "_" + str(function_index) + "_" + str(conc_index) + "_" + str(cpu_index) + "_" + str(timeout_index) + "_" + create_random_name(5) + ".txt"
    filename = filenames[workflow_name]
    spec = {}
    #if timeout_index != '-':
    #    spec['timeout'] = timeout[timeout_index]
    if conc_index != '-':
        spec['concurrency'] = conc[conc_index]
    if cpu_index != '-':
        spec['cpu'] = cpu[cpu_index]
    update(filename, workflow_functions[workflow_name][function_index], spec)
    result = run_workflows('argo-wf', workflow_name, filename, times, inp, pre_warm, log_file_name)
    final = log_file_name[:-4] + " " +  analyze_result(list(result.values()), 1)
    return final

def main():
    inp = {"src_name": "0", "DOP": "30", "detect_prob": 2}
    pprint(run('video', 3, 2, 0, '-', 3, inp, True)) 

if __name__ == "__main__":
    main()

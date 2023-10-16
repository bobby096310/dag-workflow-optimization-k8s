from pprint import pprint
from datetime import datetime
import requests
import time
from multiprocessing import Process, Manager

url = "http://10.101.174.44"

def execute(func, data):
    headers = {"Content-Type": "application/json; charset=utf-8", "Host": func + ".default.svc.cluster.local"}
    start_time = datetime.now()
    resp = requests.post(url, headers=headers, json=data)
    if 'dummy' in data:
        return
    while (not resp.ok):
        print("Retry")
        time.sleep(0.5)
        resp = requests.post(url, headers=headers, json=data)
    end_time = datetime.now()
    lat = int((end_time-start_time).total_seconds()*1000)
    result = resp.json()['Result']
    pprint(result)
    return result, lat

def execute_map(func, data, out_list, lat_list):
    if 'dummy' in data:
        return
    exec_result, lat = execute(func, data)
    out_list.append(exec_result)
    lat_list.append(lat)

def map(func, input_raw, timeout=None):
    manager = Manager()
    out_list = manager.list()
    lat_list = manager.list()
    ths=[]
    in_list = input_raw['detail']['indeces']
    for inp in in_list:
        ths.append((Process(target=execute_map,  args=(func, inp, out_list, lat_list)), inp))
    for t in ths:
        (p, a) = t
        p.start()
    for t in ths:
        (p, a) = t
        p.join()
    if (len(out_list) == 0):
        return
    return list(out_list), max(list(lat_list))
    
def run_step(func, data):
    if 'detail' in data:
        return map(func, data, timeout=None)
    else:
        return execute(func, data)

def pre_warm(func, width):
    dummy = {"detail":{"indeces":["{'dummy': 1}" for i in range(width)]}}
    run_step(func, dummy)

def run_video(inp, prewarm):
    latencies = []
    start_time = datetime.now()
    width = int(inp['DOP'])

    latencies.append("split")
    re1, lat1 = run_step('vi-split', inp)
    
    if prewarm:
        pre_warm('vi-extract', width)
        pre_warm('vi-shuffle', 1)
        pre_warm('vi-classify', width)
    
    latencies.append(str(lat1))

    latencies.append("extract")
    re2, lat2 = run_step('vi-extract', re1)
    latencies.append(str(lat2))

    latencies.append("shuffle")
    re3, lat3 = run_step('vi-shuffle', re2)
    latencies.append(str(lat3))

    latencies.append("classify")
    re4, lat4 = run_step('vi-classify', re3)
    latencies.append(str(lat4))

    end_time = datetime.now()
    latencies.append("E2E {:d}".format(int((end_time-start_time).total_seconds()*1000)))
    return (" ".join(latencies))

def run_ml(inp, prewarm):
    latencies = []
    start_time = datetime.now()
    width = 16 / int(inp['bundle_size'])

    latencies.append("pca")
    re1, lat1 = run_step('ml-pca', inp)
    if prewarm:
        pre_warm('ml-param-tune', width)
        pre_warm('ml-combine', 1)
    latencies.append(str(lat1))

    latencies.append("param-tune")
    re2, lat2 = run_step('ml-param-tune', re1)
    latencies.append(str(lat2))

    latencies.append("combine")
    re3, lat3 = run_step('ml-combine', re2)
    latencies.append(str(lat3))

    end_time = datetime.now()
    latencies.append("E2E {:d}".format(int((end_time-start_time).total_seconds()*1000)))
    return (" ".join(latencies))

def main():
    inp = {"src_name": "00", "DOP": "15", "detect_prob": 2}
    print(run_video(inp, True))

if __name__ == "__main__":
    main()

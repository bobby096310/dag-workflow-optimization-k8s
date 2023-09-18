from pprint import pprint
from datetime import datetime
import requests
import time
from multiprocessing import Process, Manager

url = "http://10.102.102.237"

def execute(func, data):
    headers = {"Content-Type": "application/json; charset=utf-8", "Host": func + ".default.svc.cluster.local"}
    start_time = datetime.now()
    resp = requests.post(url, headers=headers, json=data)
    while (not resp.ok):
        print("Retry")
        time.sleep(0.5)
        resp = requests.post(url, headers=headers, json=data)
    end_time = datetime.now()
    #pprint(resp.text)
    lat = int((end_time-start_time).total_seconds()*1000)
    result = resp.json()['Result']
    pprint(result)
    return result, lat

def execute_map(func, data, out_list, lat_list):
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
    return list(out_list), max(list(lat_list))
    '''
    ths2 = []
    for t in ths:
        (p, a) = t
        p.join(timeout)
        time.sleep(0.5)
        #print(p)
        if p.is_alive():
            # terminate the process
            p.terminate()
            print(str(p), " timeout, joining 2nd batch")
            ths2.append((Process(target=execute_map,  args=(func, inp, out_list, lat_list)), a))
        elif p.exitcode < 0:
            print(str(t), " failed, joining 2nd batch")
            ths2.append((Process(target=execute_map,  args=(func, inp, out_list, lat_list)), a))
    for t2 in ths2:
        (p2, a2) = t2
        p2.start()
    for t2 in ths2:
        (p2, a2) = t2
        p2.join()
    '''
    
def run_step(func, data):
    if 'detail' in data:
        return map(func, data, timeout=None)
    else:
        return execute(func, data)

def run_video(inp):
    latencies = []
    start_time = datetime.now()

    latencies.append("split")
    re1, lat1 = run_step('vi-split', inp)
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

def main():
    inp = {"src_name": "0", "DOP": "30", "detect_prob": 2}
    print(run_video(input))

if __name__ == "__main__":
    main()
